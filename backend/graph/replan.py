from backend.agents.budget import budget_agent
from backend.agents.itinerary import itinerary_agent
from backend.graph.builder import get_graph


async def replan(thread_id: str, selected_transport: str) -> dict:
    """User picked another transport option: rerun only Budget and Itinerary."""
    graph = await get_graph()
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await graph.aget_state(config)
    if not snapshot.values:
        raise ValueError("Plan not found or expired. Please create a new plan.")

    state = dict(snapshot.values)
    names = [o["name"] for o in state.get("transport", {}).get("options", [])]
    if selected_transport not in names:
        raise ValueError(f"Unknown transport option: {selected_transport}")

    state["selected_transport"] = selected_transport
    state.update(budget_agent(state))
    if state["mode"] == "full_trip":
        state.update(await itinerary_agent(state))
    return state
