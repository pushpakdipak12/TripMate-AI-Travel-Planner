import mcp_servers.providers.hotels as hotels


def test_category_from_osm_tags():
    assert hotels.hotel_category({"stars": "5"}) == "luxury"
    assert hotels.hotel_category({"stars": "3"}) == "mid"
    assert hotels.hotel_category({"tourism": "hostel"}) == "budget"
    assert hotels.hotel_category({}) == "mid"


def test_same_hotel_same_price():
    assert hotels.estimate_price("Sea View", "Goa", "mid") == hotels.estimate_price("Sea View", "Goa", "mid")


def test_only_matching_style_and_fallback(monkeypatch):
    monkeypatch.setattr(hotels, "get_osm_hotels", lambda city: [
        {"name": "Palace", "category": "luxury"}, {"name": "Hostel One", "category": "budget"}])
    result = hotels.find_hotels("Udaipur", nights=2, travelers=3, style="budget")
    names = [h["name"] for h in result["hotels"]]
    assert "Palace" not in names and "Hostel One" in names
    assert len(result["hotels"]) == 3                 # filled with samples
    assert all(h["rooms"] == 2 for h in result["hotels"])
