from langgraph.graph import END, START, StateGraph

from backend.agents.activities import activities_agent
from backend.agents.budget import budget_agent
from backend.agents.hotel import hotel_agent
from backend.agents.itinerary import itinerary_agent
from backend.agents.query_parser import parser_agent
from backend.agents.transport import transport_agent
from backend.agents.weather import weather_agent
from backend.graph.checkpointer import create_checkpointer
from backend.graph.state import TripState
from backend.observability.tracing import timed_node
from backend.graph.supervisor import route_after_agent, route_after_budget, route_after_parser

AGENTS = ["transport", "hotels", "weather", "activities"]


def build_graph(checkpointer):
    builder = StateGraph(TripState)

    builder.add_node("parser", timed_node("parser", parser_agent))
    builder.add_node("transport", timed_node("transport", transport_agent))
    builder.add_node("hotels", timed_node("hotels", hotel_agent))
    builder.add_node("weather", timed_node("weather", weather_agent))
    builder.add_node("activities", timed_node("activities", activities_agent))
    builder.add_node("budget", timed_node("budget", budget_agent))
    builder.add_node("itinerary", timed_node("itinerary", itinerary_agent))

    builder.add_edge(START, "parser")
    builder.add_conditional_edges("parser", route_after_parser, AGENTS + [END])
    for agent in AGENTS:
        builder.add_conditional_edges(agent, route_after_agent, ["budget", END])
    builder.add_conditional_edges("budget", route_after_budget, ["hotels", "itinerary", END])
    builder.add_edge("itinerary", END)

    return builder.compile(checkpointer=checkpointer)


_graph = None


async def get_graph():
    """Builds the graph once, with a Redis (or memory) checkpointer."""
    global _graph
    if _graph is None:
        _graph = build_graph(await create_checkpointer())
    return _graph


async def close_graph():
    """Closes the SQLite connection (if used) so the program exits cleanly."""
    connection = getattr(_graph.checkpointer, "conn", None) if _graph else None
    if connection is not None and hasattr(connection, "close"):
        await connection.close()
