# Pure Python. No LLM here, so the numbers are always correct.

FOOD_PER_PERSON_DAY = {"budget": 600, "mid": 1200, "luxury": 3000}
ACTIVITIES_PER_PERSON_DAY = {"budget": 400, "mid": 1000, "luxury": 2500}
MAX_RETRIES = 2


def round_trip_cost(option: dict) -> int:
    return option["price_min"] + option["price_max"]    # average one way x 2


def find_transport_option(state: dict):
    options = state.get("transport", {}).get("options", [])
    wanted = state.get("selected_transport") or state.get("recommended_transport", {}).get("option_name")
    for option in options:
        if option["name"] == wanted:
            return option
    return None


def saving_tips(state: dict, option) -> list[str]:
    tips = []
    options = state.get("transport", {}).get("options", [])
    if option and options:
        cheapest = min(options, key=round_trip_cost)
        saving = round_trip_cost(option) - round_trip_cost(cheapest)
        if saving > 0:
            tips.append(f"Switch to {cheapest['name']} to save about ₹{saving:,}.")
    if state["trip"]["travel_style"] != "budget":
        tips.append("Choose budget travel style to lower hotel, food and activity costs.")
    tips.append("Reduce the trip by one day to save on hotel and food.")
    return tips


def budget_agent(state: dict) -> dict:
    trip = state["trip"]
    people = trip["travelers"]
    days = trip.get("days") or 1
    style = trip["travel_style"]

    option = find_transport_option(state)
    transport_cost = round_trip_cost(option) if option else 0
    hotel_cost = state.get("chosen_hotel", {}).get("total_price", 0)
    food_cost = FOOD_PER_PERSON_DAY[style] * people * days
    activities_cost = ACTIVITIES_PER_PERSON_DAY[style] * people * days
    total = transport_cost + hotel_cost + food_cost + activities_cost

    limit = trip.get("budget_inr")
    over_budget = bool(limit and total > limit)
    retries = state.get("retries", 0)
    retrying = over_budget and retries < MAX_RETRIES and not state.get("selected_transport")

    budget = {
        "transport": transport_cost,
        "transport_option": option["name"] if option else None,
        "hotel": hotel_cost,
        "food": food_cost,
        "activities": activities_cost,
        "total": total,
        "limit": limit,
        "over_budget": over_budget,
        "difference": (limit - total) if limit else None,
        "retrying": retrying,
        "tips": saving_tips(state, option) if over_budget and not retrying else [],
    }
    return {"budget": budget, "retries": retries + 1 if retrying else retries}
