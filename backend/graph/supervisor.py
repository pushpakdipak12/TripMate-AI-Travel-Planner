from langgraph.graph import END

# Which agents each tab needs. No LLM guessing: the tab decides.
PLAN = {
    "full_trip": ["transport", "hotels", "weather", "activities"],
    "budget": ["transport", "hotels"],
    "transport": ["transport"],
    "hotels": ["hotels"],
    "weather": ["weather"],
    "activities": ["activities"],
}


def route_after_parser(state: dict):
    """Returns a list of agents. LangGraph runs them in parallel."""
    if state.get("needs_clarification"):
        return END
    return PLAN[state["mode"]]


def route_after_agent(state: dict):
    if state["mode"] in ("full_trip", "budget"):
        return "budget"
    return END


def route_after_budget(state: dict):
    if state["budget"]["retrying"]:
        return "hotels"             # over budget: try a cheaper hotel
    if state["mode"] == "full_trip":
        return "itinerary"
    return END
