def check_output(state: dict) -> list[str]:
    """Last check before sending the plan to the user. Returns warnings."""
    warnings = []
    trip = state.get("trip") or {}

    budget = state.get("budget")
    if budget:
        parts = budget["transport"] + budget["hotel"] + budget["food"] + budget["activities"]
        if parts != budget["total"]:
            budget["total"] = parts
            warnings.append("Budget total was corrected.")

    recommended = state.get("recommended_transport")
    options = [o["name"] for o in (state.get("transport") or {}).get("options", [])]
    if recommended and recommended["option_name"] not in options:
        warnings.append("Recommended transport was not in the options list.")

    itinerary = state.get("itinerary") or []
    if itinerary and trip.get("days") and len(itinerary) != trip["days"]:
        warnings.append(f"Itinerary has {len(itinerary)} days but the trip has {trip['days']} days.")
    if any("₹" in day["plan"] or "Rs" in day["plan"] for day in itinerary):
        warnings.append("Itinerary mentions prices. Use the budget section for reliable prices.")

    return warnings
