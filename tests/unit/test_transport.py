import mcp_servers.providers.transport as transport


def options_for(km, travelers=2, monkeypatch=None):
    monkeypatch.setattr(transport, "road_distance_km", lambda a, b: km)
    return {o["name"] for o in transport.compare_transport("Pune", "Goa", travelers)["options"]}


def test_medium_trip_has_all_modes(monkeypatch):
    names = options_for(450, monkeypatch=monkeypatch)
    assert {"Train (3AC)", "Private AC sleeper bus", "Cab", "Self-drive", "Flight"} <= names


def test_long_trip_has_no_bus_or_cab(monkeypatch):
    names = options_for(1500, monkeypatch=monkeypatch)
    assert "Cab" not in names and "Government bus" not in names
    assert "Flight" in names


def test_short_trip_has_no_flight(monkeypatch):
    names = options_for(150, monkeypatch=monkeypatch)
    assert "Flight" not in names


def test_price_scales_with_travelers(monkeypatch):
    monkeypatch.setattr(transport, "road_distance_km", lambda a, b: 450)
    one = transport.compare_transport("Pune", "Goa", 1)["options"][0]["price_min"]
    four = transport.compare_transport("Pune", "Goa", 4)["options"][0]["price_min"]
    assert four >= 3 * one


def test_unknown_city_returns_error(monkeypatch):
    monkeypatch.setattr(transport, "road_distance_km", lambda a, b: None)
    assert "error" in transport.compare_transport("Nowhere", "Goa", 2)
