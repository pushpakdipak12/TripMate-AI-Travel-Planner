from backend.agents.budget import budget_agent

OPTIONS = [
    {"name": "Train (Sleeper)", "price_min": 500, "price_max": 800},
    {"name": "Flight", "price_min": 6000, "price_max": 11000},
]


def make_state(budget_inr, retries=0, selected=None):
    return {
        "trip": {"travelers": 2, "days": 3, "travel_style": "mid", "budget_inr": budget_inr},
        "transport": {"options": OPTIONS},
        "recommended_transport": {"option_name": "Flight"},
        "selected_transport": selected,
        "chosen_hotel": {"total_price": 8000},
        "retries": retries,
    }


def test_total_is_sum_of_parts():
    budget = budget_agent(make_state(100000))["budget"]
    assert budget["total"] == budget["transport"] + budget["hotel"] + budget["food"] + budget["activities"]
    assert budget["transport"] == 17000          # round trip = min + max
    assert budget["over_budget"] is False


def test_over_budget_triggers_retry():
    result = budget_agent(make_state(20000))
    assert result["budget"]["over_budget"] is True
    assert result["budget"]["retrying"] is True
    assert result["retries"] == 1


def test_no_more_retries_after_limit_gives_tips():
    result = budget_agent(make_state(20000, retries=2))
    assert result["budget"]["retrying"] is False
    assert any("Train (Sleeper)" in tip for tip in result["budget"]["tips"])


def test_user_selection_wins_over_recommendation():
    budget = budget_agent(make_state(100000, selected="Train (Sleeper)"))["budget"]
    assert budget["transport_option"] == "Train (Sleeper)"
