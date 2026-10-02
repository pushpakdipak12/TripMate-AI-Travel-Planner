import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from backend import config
from backend.agents.query_parser import parse_query
from backend.api.schemas import ParseRequest, PlanRequest, ReplanRequest
from backend.cache.rate_limiter import is_allowed
from backend.cache.redis_client import get_redis
from backend.graph.builder import get_graph
from backend.graph.replan import replan
from backend.guardrails.input_checks import InputRejected, check_input
from backend.guardrails.output_checks import check_output
from backend.models.trip_query import ParseResult
from backend.observability.logging import log_event, request_id_var
from backend.observability.metrics import record_plan, snapshot
from backend.observability.tracing import run_config

router = APIRouter()

RESPONSE_FIELDS = [
    "mode", "trip", "needs_clarification", "question", "transport", "recommended_transport",
    "selected_transport", "hotels", "chosen_hotel", "weather", "activities", "budget",
    "itinerary", "errors",
]


def rate_limit(request: Request):
    user_key = request.client.host if request.client else "unknown"
    if not is_allowed(user_key):
        raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute.")


def safe_query(query: str) -> str:
    try:
        return check_input(query)
    except InputRejected as e:
        log_event("input blocked", reason=str(e))
        raise HTTPException(status_code=400, detail=str(e))


def to_response(thread_id: str, state: dict) -> dict:
    response = {field: state.get(field) for field in RESPONSE_FIELDS}
    response["thread_id"] = thread_id
    response["warnings"] = check_output(state)
    return response


@router.get("/health")
async def health():
    graph = await get_graph()
    storage = type(graph.checkpointer).__name__.replace("Async", "").replace("Saver", "")
    return {"status": "ok", "redis": get_redis() is not None, "plan_storage": storage, "model": config.GROQ_MODEL}


@router.get("/stats")
def stats():
    """Numbers for the Monitoring page."""
    data = snapshot()
    client = get_redis()
    hits = int(client.get("stats:cache:hit") or 0) if client else 0
    misses = int(client.get("stats:cache:miss") or 0) if client else 0
    data["cache"] = {"hits": hits, "misses": misses,
                     "hit_ratio": round(hits / (hits + misses), 2) if hits + misses else None}
    data["model"] = config.GROQ_MODEL
    return data


@router.post("/parse", response_model=ParseResult, dependencies=[Depends(rate_limit)])
def parse(request: ParseRequest):
    query = safe_query(request.query)
    try:
        return parse_query(query, request.mode)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")


@router.post("/plan", dependencies=[Depends(rate_limit)])
async def plan(request: PlanRequest):
    query = safe_query(request.query)
    graph = await get_graph()
    thread_id = str(uuid.uuid4())
    run = run_config(thread_id, request.mode, request_id_var.get())
    try:
        state = await graph.ainvoke({"mode": request.mode, "query": query, "retries": 0, "errors": []}, run)
    except Exception as e:
        record_plan(request.mode, "error")
        log_event("plan failed", mode=request.mode, error=str(e)[:200])
        raise HTTPException(status_code=502, detail=f"Planning failed: {e}")

    outcome = "clarification" if state.get("needs_clarification") else "ok"
    record_plan(request.mode, outcome)
    log_event("plan done", mode=request.mode, outcome=outcome, thread_id=thread_id)
    return to_response(thread_id, state)


@router.post("/replan", dependencies=[Depends(rate_limit)])
async def replan_route(request: ReplanRequest):
    try:
        state = await replan(request.thread_id, request.selected_transport)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    record_plan(state["mode"], "replan")
    return to_response(request.thread_id, state)
