from langgraph.graph import END

from backend.graph.supervisor import route_after_agent, route_after_budget, route_after_parser


def test_full_trip_runs_four_agents_in_parallel():
    assert route_after_parser({"mode": "full_trip"}) == ["transport", "hotels", "weather", "activities"]


def test_single_tab_runs_one_agent():
    assert route_after_parser({"mode": "weather"}) == ["weather"]


def test_clarification_stops_the_graph():
    assert route_after_parser({"mode": "full_trip", "needs_clarification": True}) == END


def test_budget_loop_and_itinerary():
    assert route_after_agent({"mode": "hotels"}) == END
    assert route_after_agent({"mode": "full_trip"}) == "budget"
    assert route_after_budget({"mode": "full_trip", "budget": {"retrying": True}}) == "hotels"
    assert route_after_budget({"mode": "full_trip", "budget": {"retrying": False}}) == "itinerary"
    assert route_after_budget({"mode": "budget", "budget": {"retrying": False}}) == END
