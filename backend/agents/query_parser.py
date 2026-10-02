from datetime import date

from backend.guardrails.india_check import is_indian_place
from backend.guardrails.input_checks import check_trip_limits
from backend.llm.provider import get_structured_llm
from backend.models.trip_query import Mode, ParseResult, TripQuery
from backend.prompts.parser_prompt import parser_prompt

REQUIRED_FIELDS = {
    "full_trip": ["origin", "destination", "days"],
    "transport": ["origin", "destination"],
    "hotels": ["destination"],
    "weather": ["destination"],
    "activities": ["destination"],
    "budget": ["destination", "days"],
}

QUESTIONS = {
    "origin": "Where are you starting from?",
    "destination": "Where do you want to go?",
    "days": "How many days is the trip?",
}


def find_missing(trip: TripQuery, mode: Mode) -> list[str]:
    return [field for field in REQUIRED_FIELDS[mode] if not getattr(trip, field)]


def parse_query(query: str, mode: Mode) -> ParseResult:
    chain = parser_prompt | get_structured_llm(TripQuery)
    trip = chain.invoke({"query": query, "today": date.today().isoformat()})

    places = [p for p in (trip.origin, trip.destination) if p]
    not_india = [p for p in places if not is_indian_place(p)]
    if not_india:
        return ParseResult(
            mode=mode,
            trip=trip,
            needs_clarification=True,
            question=f"Sorry, we only plan trips within India. Not supported: {', '.join(not_india)}.",
        )

    limit_problem = check_trip_limits(trip)
    if limit_problem:
        return ParseResult(mode=mode, trip=trip, needs_clarification=True, question=limit_problem)

    missing = find_missing(trip, mode)
    if missing:
        return ParseResult(
            mode=mode,
            trip=trip,
            missing_fields=missing,
            needs_clarification=True,
            question=" ".join(QUESTIONS[f] for f in missing),
        )

    return ParseResult(mode=mode, trip=trip)


def parser_agent(state: dict) -> dict:
    """LangGraph node: turns the query into a trip dict."""
    result = parse_query(state["query"], state["mode"])
    return {
        "trip": result.trip.model_dump(),
        "needs_clarification": result.needs_clarification,
        "question": result.question,
    }
