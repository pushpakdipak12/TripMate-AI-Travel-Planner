from backend.llm.provider import get_structured_llm
from backend.models.plan import Itinerary
from backend.prompts.itinerary_prompt import itinerary_prompt

INDOOR_TYPES = {"museum", "palace", "monument"}
OUTDOOR_TYPES = {"beach", "viewpoint", "fort", "castle", "attraction"}


def describe_place(place: dict) -> str:
    place_type = place.get("type") or "place"
    if place_type in INDOOR_TYPES:
        setting = "indoor"
    elif place_type in OUTDOOR_TYPES:
        setting = "outdoor"
    else:
        setting = "indoor or outdoor"
    return f"- {place['name']} ({place_type}, {setting})"


async def itinerary_agent(state: dict) -> dict:
    trip = state["trip"]
    weather = [
        f"Day {i + 1} ({d['date']}): {d['condition']}, rain {d['rain_chance_pct']}%"
        for i, d in enumerate(state.get("weather", {}).get("forecast", []))
    ]
    places = [describe_place(p) for p in state.get("activities", {}).get("places", [])]

    chain = itinerary_prompt | get_structured_llm(Itinerary)
    result = await chain.ainvoke({
        "days": trip["days"],
        "trip": trip,
        "interests": ", ".join(trip.get("interests") or []) or "general sightseeing",
        "transport": state.get("budget", {}).get("transport_option"),
        "hotel": state.get("chosen_hotel", {}).get("name"),
        "weather": weather or "Not available",
        "places": "\n".join(places) or "Not available, suggest general local experiences",
    })
    return {"itinerary": [day.model_dump() for day in result.days]}
