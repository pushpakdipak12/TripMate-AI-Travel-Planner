"""
Creates preview.html: a static TripMate page with sample Goa data.
Open it in any browser or send it to a client. No backend needed.

    python -m scripts.make_preview
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "frontend"))
import components as ui  # noqa: E402

parts = []
ui.html = parts.append

SAMPLE = {
    "trip": {"origin": "Pune", "destination": "Goa", "start_date": "2026-10-08", "days": 4, "travelers": 2,
             "budget_inr": 40000, "travel_style": "mid", "interests": ["beaches", "seafood"]},
    "transport": {"distance_km": 440, "price_basis": "One way, total for all travellers, estimated", "options": [
        {"name": "Train (Sleeper)", "mode": "train", "duration_hours": 10.5, "price_min": 450, "price_max": 750, "note": "Cheapest, less comfortable"},
        {"name": "Train (3AC)", "mode": "train", "duration_hours": 10.5, "price_min": 1150, "price_max": 1500, "note": "Comfortable, good value"},
        {"name": "Private AC sleeper bus", "mode": "bus", "duration_hours": 10.5, "price_min": 1400, "price_max": 2350, "note": "Many departures, overnight option"},
        {"name": "Self-drive", "mode": "self_drive", "duration_hours": 7.9, "price_min": 3800, "price_max": 5200, "note": "Fuel and tolls, flexible"},
        {"name": "Flight", "mode": "flight", "duration_hours": 3.7, "price_min": 6350, "price_max": 11450, "note": "Fastest, includes airport time"}]},
    "recommended_transport": {"option_name": "Train (3AC)",
                              "reason": "Comfortable overnight travel at a fair price for two, leaving more of the budget for your stay."},
    "selected_transport": None,
    "chosen_hotel": {"name": "Menino Regency", "price_per_room_night": 5300, "rooms": 1, "total_price": 15900},
    "hotels": {"nights": 3, "source": "Names from OpenStreetMap, prices estimated", "hotels": [
        {"name": "Hotel Mandovi", "price_per_room_night": 4200, "rooms": 1, "total_price": 12600},
        {"name": "Menino Regency", "price_per_room_night": 5300, "rooms": 1, "total_price": 15900},
        {"name": "Panjim Inn", "price_per_room_night": 6100, "rooms": 1, "total_price": 18300}]},
    "weather": {"source": "Weather data by Open-Meteo.com", "forecast": [
        {"date": "2026-10-08", "condition": "Partly cloudy", "max_temp_c": 31.6, "min_temp_c": 25.2, "rain_chance_pct": 20},
        {"date": "2026-10-09", "condition": "Light drizzle", "max_temp_c": 30.4, "min_temp_c": 25.0, "rain_chance_pct": 65},
        {"date": "2026-10-10", "condition": "Thunderstorm", "max_temp_c": 29.8, "min_temp_c": 24.6, "rain_chance_pct": 85},
        {"date": "2026-10-11", "condition": "Mostly clear", "max_temp_c": 32.1, "min_temp_c": 25.4, "rain_chance_pct": 10}]},
    "activities": {"source": "Popular places + OpenStreetMap", "places":
        [{"name": n, "type": "popular"} for n in ("Calangute Beach", "Baga Beach", "Fort Aguada", "Basilica of Bom Jesus")]
        + [{"name": "Museum of Goa", "type": "museum"}, {"name": "Reis Magos Fort", "type": "fort"},
           {"name": "Miramar Beach", "type": "beach"}]},
    "budget": {"transport": 2650, "transport_option": "Train (3AC)", "hotel": 15900, "food": 9600, "activities": 8000,
               "total": 36150, "limit": 40000, "over_budget": False, "difference": 3850, "tips": []},
    "itinerary": [
        {"day": 1, "title": "Arrival and Calangute sunset", "plan": "Arrive by overnight train and check in at Menino Regency. Afternoon at Calangute Beach, then a seafood dinner by the shore."},
        {"day": 2, "title": "Old Goa heritage", "plan": "A drizzly day for indoor sights: Basilica of Bom Jesus in the morning, Museum of Goa after lunch, and a cafe evening in Fontainhas."},
        {"day": 3, "title": "Forts and coastal views", "plan": "Storms expected, so start late. Reis Magos Fort when the rain eases (weather permitting), then a long Goan seafood lunch."},
        {"day": 4, "title": "Baga Beach and home", "plan": "The driest day: morning at Baga Beach and Fort Aguada, then check out and board the evening train back to Pune."}],
    "warnings": [], "errors": [],
}


def capture(*steps) -> str:
    start = len(parts)
    for step in steps:
        step()
    block = "".join(parts[start:])
    del parts[start:]
    return f"<div>{block}</div>"


def two_columns(left: str, right: str):
    parts.append(f'<div style="display:grid;grid-template-columns:3fr 2fr;gap:2.5rem">{left}{right}</div>')


plan = SAMPLE
ui.brand({"redis": True, "plan_storage": "Redis"})
ui.ticket("full_trip", plan)
ui.summary_strip(plan)
two_columns(capture(lambda: ui.section("How to get there"), lambda: ui.transport_table(plan), lambda: ui.recommendation(plan)),
            capture(lambda: ui.section("Budget"), lambda: ui.budget_panel(plan["budget"])))
ui.section("Weather during your trip")
ui.weather_strip(plan["weather"])
two_columns(capture(lambda: ui.section("Where to stay"), lambda: ui.hotels_table(plan["hotels"], plan["chosen_hotel"])),
            capture(lambda: ui.section("Places to visit"), lambda: ui.places_chips(plan["activities"])))
two_columns(capture(lambda: ui.section("Day-by-day plan"), lambda: ui.itinerary_timeline(plan["itinerary"], plan["trip"])),
            capture(lambda: ui.section("Notes"), lambda: ui.trip_notes(plan)))
ui.footer()

css = (Path(__file__).resolve().parents[1] / "frontend" / "styles.css").read_text(encoding="utf-8")
page = (
    '<!doctype html><html><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1"><title>TripMate preview</title>'
    f'<style>{css} body{{margin:0;background:var(--paper);font-family:Inter,system-ui,sans-serif;color:var(--ink)}}'
    '.wrap{max-width:1440px;margin:0 auto;padding:28px 48px 56px}</style></head>'
    f'<body><div class="wrap">{"".join(parts)}</div></body></html>'
)
Path("preview.html").write_text(page, encoding="utf-8")
print("Created preview.html. Open it in your browser.")
