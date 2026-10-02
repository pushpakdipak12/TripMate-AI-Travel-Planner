import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from prometheus_client import make_asgi_app

from backend.api.routes import router
from backend.graph.builder import close_graph, get_graph
from backend.observability.logging import log_event, request_id_var
from backend.observability.metrics import record_request

KNOWN_PATHS = {"/plan", "/replan", "/parse", "/health", "/stats"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_graph()       # connect Redis and build the graph once at startup
    log_event("server started")
    yield
    await close_graph()


app = FastAPI(title="TripMate · India Travel Planner", lifespan=lifespan)
app.include_router(router)
app.mount("/metrics", make_asgi_app())      # Prometheus scrapes this


@app.middleware("http")
async def observe_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    token = request_id_var.set(request_id)
    path = request.url.path if request.url.path in KNOWN_PATHS else "other"
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        seconds = time.perf_counter() - start
        if path != "other":
            record_request(path, status, seconds)
            log_event("request", path=path, status=status, ms=round(seconds * 1000))
        request_id_var.reset(token)
