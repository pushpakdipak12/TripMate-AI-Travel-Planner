from backend.tools.mcp_client import call_tool

CHEAPER_STYLE = {"luxury": "mid", "mid": "budget", "budget": "budget"}


def count_nights(state: dict) -> int:
    days = state["trip"].get("days") or 1
    if state["mode"] == "hotels":
        return days                 # "3 nights" -> 3
    return max(1, days - 1)         # 5-day trip -> 4 nights


async def hotel_agent(state: dict) -> dict:
    trip = state["trip"]
    retries = state.get("retries", 0)
    style = trip["travel_style"]
    if retries >= 2:
        style = CHEAPER_STYLE[style]    # second retry: go one level cheaper

    result = await call_tool("search_hotels", {
        "city": trip["destination"],
        "nights": count_nights(state),
        "travelers": trip["travelers"],
        "style": style,
    })
    hotels = result.get("hotels", [])
    if not hotels:
        return {"hotels": result, "errors": ["Hotels: none found"]}

    # Normally pick a middle option. When over budget, pick the cheapest.
    chosen = hotels[0] if retries > 0 else hotels[len(hotels) // 2]
    return {"hotels": result, "chosen_hotel": chosen}
