"""HTML building blocks for the TripMate UI. All text from the backend is escaped."""
from datetime import date, timedelta
from html import escape

import streamlit as st

MODE_ICONS = {"train": "🚆", "bus": "🚌", "cab": "🚕", "self_drive": "🚗", "flight": "✈️"}
PLACE_ICONS = {
    "beach": "🏖️", "fort": "🏰", "castle": "🏰", "palace": "🏯", "museum": "🏛️",
    "monument": "🗿", "viewpoint": "🌄", "attraction": "📍", "popular": "⭐", "suggested": "✨",
}
STYLE_NAMES = {"budget": "Budget", "mid": "Mid-range", "luxury": "Luxury"}


# ---------- small helpers ----------

def html(markup: str):
    st.markdown(markup, unsafe_allow_html=True)


def rupees(amount) -> str:
    return f"₹{amount:,}" if amount is not None else "–"


def fare(option: dict) -> str:
    return f"{rupees(option['price_min'])} – {rupees(option['price_max'])}"


def hours(value: float) -> str:
    whole = int(value)
    minutes = round((value - whole) * 60)
    return f"{whole} h {minutes:02d} m" if minutes else f"{whole} h"


def weather_icon(condition: str) -> str:
    text = condition.lower()
    if "thunder" in text:
        return "⛈️"
    if any(word in text for word in ("rain", "drizzle", "shower")):
        return "🌧️"
    if "fog" in text:
        return "🌫️"
    if "cloudy" in text and "partly" not in text:
        return "☁️"
    if "partly" in text or "mostly" in text:
        return "⛅"
    return "☀️"


def trip_dates(trip: dict):
    if not trip.get("start_date"):
        return None
    try:
        start = date.fromisoformat(trip["start_date"])
    except ValueError:
        return None
    end = start + timedelta(days=max(1, trip.get("days") or 1) - 1)
    return start, end


def current_transport(result: dict) -> str | None:
    return result.get("selected_transport") or (result.get("recommended_transport") or {}).get("option_name")


def section(title: str):
    html(f'<div class="section-title">{escape(title)}</div>')


def source(text: str | None):
    if text:
        html(f'<div class="source">{escape(text)}</div>')


# ---------- page parts ----------

LOGO = (
    '<svg class="logo-mark" viewBox="0 0 40 40" aria-hidden="true">'
    '<circle cx="20" cy="20" r="19" fill="#F2A516"/>'
    '<circle cx="20" cy="20" r="14" fill="#0F1E46"/>'
    '<path d="M20 9 L24 20 L20 31 L16 20 Z" fill="#F2A516"/>'
    '<path d="M20 20 L24 20 L20 31 Z" fill="#FFD27A"/>'
    '<circle cx="20" cy="20" r="2" fill="#0F1E46"/>'
    '</svg>'
)


def brand(status: dict | None):
    if status:
        redis_on = status.get("redis")
        badges = (
            '<span class="badge"><span class="dot"></span>Planner online</span>'
            f'<span class="badge"><span class="dot{"" if redis_on else " off"}"></span>'
            f'{"Fast cache on" if redis_on else "Cache off"}</span>'
            f'<span class="badge">Plans saved in {escape(status.get("plan_storage", "-"))}</span>'
        )
    else:
        badges = '<span class="badge"><span class="dot off"></span>Planner offline</span>'
    html(
        '<div class="hero"><div>'
        f'<div class="logo">{LOGO}<div class="logo-name">Trip<span>Mate</span></div></div>'
        '<div class="hero-tag">Your travel companion for India. Transport, stays, weather and '
        'a day-by-day plan, ready in one place.</div>'
        f'</div><div class="status">{badges}</div></div>'
    )


def hint(query_format: str, example: str):
    html(
        f'<div class="hint"><span><b>How to write:</b> {escape(query_format)}</span>'
        f'<span><b>Example:</b> <span class="ex">{escape(example)}</span></span>'
        '<span>Date is optional. Weather covers 16 days ahead.</span></div>'
    )


def empty_state(text: str):
    html(f'<div class="empty"><b>Your plan will appear here</b>{escape(text)}</div>')


def ticket(mode: str, result: dict):
    trip = result["trip"]
    origin, destination = trip.get("origin"), trip.get("destination") or "–"
    transport = result.get("transport") or {}

    if mode in ("full_trip", "transport", "budget") and origin:
        icon = MODE_ICONS.get(_mode_of(result), "🧭")
        km = transport.get("distance_km")
        main = (
            '<div class="ticket-main">'
            f'<div><div class="t-label">From</div><div class="t-city">{escape(origin)}</div></div>'
            f'<div class="t-route"><div class="t-line">{icon}</div>'
            f'<div class="t-km">{f"{km:,} km by road" if km else "Route"}</div></div>'
            f'<div class="t-to"><div class="t-label">To</div><div class="t-city">{escape(destination)}</div></div>'
            '</div>'
        )
    else:
        label = {"hotels": "Stay in", "weather": "Weather in", "activities": "Explore"}.get(mode, "Trip to")
        main = (f'<div class="ticket-main single"><div><div class="t-label">{label}</div>'
                f'<div class="t-city">{escape(destination)}</div></div></div>')

    dates = trip_dates(trip)
    last = ("Budget", rupees(trip["budget_inr"])) if trip.get("budget_inr") else \
        ("Style", STYLE_NAMES.get(trip.get("travel_style"), "Mid-range"))
    facts = [
        ("Dates", f"{dates[0]:%d %b} – {dates[1]:%d %b %Y}" if dates else "Flexible"),
        ("Duration", f"{trip['days']} days" if trip.get("days") else "–"),
        ("Travellers", str(trip.get("travelers", 1))),
        last,
    ]
    stub = "".join(f'<div><div class="s-label">{k}</div><div class="s-value num">{escape(v)}</div></div>'
                   for k, v in facts)
    html(f'<div class="ticket">{main}<div class="ticket-stub">{stub}</div></div>')


def _mode_of(result: dict) -> str:
    name = current_transport(result)
    for option in (result.get("transport") or {}).get("options", []):
        if option["name"] == name:
            return option["mode"]
    return ""


def summary_strip(result: dict):
    budget = result.get("budget") or {}
    hotel = result.get("chosen_hotel") or {}
    forecast = (result.get("weather") or {}).get("forecast", [])

    total, limit = budget.get("total"), budget.get("limit")
    if limit:
        used = min(100, round(total / limit * 100))
        over = budget.get("over_budget")
        cost_sub = f"of {rupees(limit)} budget"
        cost_bar = f'<div class="bar{" over" if over else ""}"><span style="width:{used}%"></span></div>'
    else:
        cost_sub, cost_bar = "Estimated for the whole trip", ""

    rainy = sum(1 for d in forecast if d["rain_chance_pct"] and d["rain_chance_pct"] >= 60)
    if forecast:
        avg = round(sum(d["max_temp_c"] for d in forecast) / len(forecast))
        weather_value = f"{avg}°C average"
        weather_sub = f"{rainy} of {len(forecast)} days likely rainy" if rainy else "Mostly dry days"
    else:
        weather_value, weather_sub = "Not available", "Forecast covers 16 days ahead"

    option = current_transport(result) or "–"
    html(
        '<div class="strip">'
        f'<div><div class="k-label">Estimated total</div><div class="k-value big num">{rupees(total)}</div>'
        f'<div class="k-sub">{cost_sub}</div>{cost_bar}</div>'
        f'<div><div class="k-label">Travel by</div><div class="k-value">{escape(option)}</div>'
        f'<div class="k-sub">Round trip {rupees(budget.get("transport"))}</div></div>'
        f'<div><div class="k-label">Stay</div><div class="k-value">{escape(hotel.get("name", "–"))}</div>'
        f'<div class="k-sub">{rupees(hotel.get("price_per_room_night"))} per night</div></div>'
        f'<div><div class="k-label">Weather</div><div class="k-value">{weather_value}</div>'
        f'<div class="k-sub">{weather_sub}</div></div>'
        '</div>'
    )


def transport_table(result: dict):
    transport = result.get("transport") or {}
    options = transport.get("options", [])
    if not options:
        html(f'<div class="callout warn">{escape(transport.get("error", "No transport options found for this route."))}</div>')
        return
    recommended = (result.get("recommended_transport") or {}).get("option_name")
    chosen = current_transport(result)
    rows = ""
    for o in options:
        tags = ""
        if o["name"] == recommended:
            tags += '<span class="pill rec">Recommended</span>'
        if o["name"] == chosen and chosen != recommended:
            tags += '<span class="pill sel">Selected</span>'
        rows += (
            f'<tr class="{"sel" if o["name"] == chosen else ""}">'
            f'<td><span class="opt">{MODE_ICONS.get(o["mode"], "")} {escape(o["name"])}</span>{tags}</td>'
            f'<td class="num">{hours(o["duration_hours"])}</td>'
            f'<td class="r num">{fare(o)}</td>'
            f'<td class="note">{escape(o["note"])}</td></tr>'
        )
    html(
        '<div class="panel"><table class="data"><thead><tr>'
        '<th>Option</th><th>Travel time</th><th class="r">Fare, one way</th><th>Good to know</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>'
    )
    source(f"{transport.get('price_basis', '')}. Fares are estimates based on distance.")


def recommendation(result: dict):
    rec = result.get("recommended_transport")
    if rec:
        html(f'<div class="callout"><b>Why {escape(rec["option_name"])}:</b> {escape(rec["reason"])}</div>')


def budget_panel(budget: dict):
    if not budget:
        return
    rows = [
        ("Transport", budget.get("transport_option") or "", budget["transport"]),
        ("Hotel", "", budget["hotel"]),
        ("Food", "", budget["food"]),
        ("Activities", "", budget["activities"]),
    ]
    body = "".join(
        f'<div class="b-row"><span>{name}<span class="note">{escape(detail)}</span></span>'
        f'<span class="num">{rupees(amount)}</span></div>'
        for name, detail, amount in rows
    )
    body += f'<div class="b-total"><span>Total</span><span class="num">{rupees(budget["total"])}</span></div>'

    if budget.get("limit"):
        used = min(100, round(budget["total"] / budget["limit"] * 100))
        if budget["over_budget"]:
            body += f'<div class="bar over"><span style="width:{used}%"></span></div>'
            body += f'<div class="b-status bad">Over budget by {rupees(-budget["difference"])}</div>'
            tips = "".join(f"<li>{escape(tip)}</li>" for tip in budget.get("tips", []))
            if tips:
                body += f'<ul class="tips">{tips}</ul>'
        else:
            body += f'<div class="bar"><span style="width:{used}%"></span></div>'
            body += f'<div class="b-status good">Within budget, {rupees(budget["difference"])} to spare</div>'
    html(f'<div class="panel pad">{body}</div>')
    source("Round-trip transport. Food and activities estimated per person per day.")


def weather_strip(weather: dict):
    weather = weather or {}
    forecast = weather.get("forecast", [])
    if not forecast:
        html(f'<div class="callout info">{escape(weather.get("note") or weather.get("error") or "Weather is not available.")}</div>')
        return
    tiles = ""
    for d in forecast:
        try:
            label = f'{date.fromisoformat(d["date"]):%a, %d %b}'
        except ValueError:
            label = d["date"]
        rain = d["rain_chance_pct"] or 0
        tiles += (
            f'<div class="wx-day{" wet" if rain >= 60 else ""}">'
            f'<div class="wx-date">{escape(label)}</div>'
            f'<div class="wx-icon">{weather_icon(d["condition"])}</div>'
            f'<div class="wx-temp num">{d["max_temp_c"]:.0f}° <small>/ {d["min_temp_c"]:.0f}°</small></div>'
            f'<div class="wx-cond">{escape(d["condition"])}</div>'
            f'<div class="wx-rain">Rain {rain}%<div class="bar"><span style="width:{rain}%"></span></div></div>'
            '</div>'
        )
    html(f'<div class="wx">{tiles}</div>')
    source(weather.get("source"))


def hotels_table(hotels: dict, chosen: dict | None):
    items = (hotels or {}).get("hotels", [])
    if not items:
        html('<div class="callout warn">No hotels found for this city.</div>')
        return
    rows = ""
    for h in items:
        picked = chosen and h["name"] == chosen["name"]
        tag = '<span class="pill sel">Selected</span>' if picked else ""
        rows += (
            f'<tr class="{"sel" if picked else ""}">'
            f'<td><span class="opt">{escape(h["name"])}</span>{tag}</td>'
            f'<td class="r num">{rupees(h["price_per_room_night"])}</td>'
            f'<td class="r num">{h["rooms"]}</td>'
            f'<td class="r num">{rupees(h["total_price"])}</td></tr>'
        )
    nights = hotels.get("nights")
    html(
        '<div class="panel"><table class="data"><thead><tr>'
        f'<th>Hotel</th><th class="r">Per night</th><th class="r">Rooms</th><th class="r">Total, {nights} night(s)</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>'
    )
    source(hotels.get("source"))


def places_chips(activities: dict):
    activities = activities or {}
    places = activities.get("places", [])
    if not places:
        html(f'<div class="callout warn">{escape(activities.get("note", "No places found."))}</div>')
        return
    chips = "".join(
        f'<span class="chip{" top" if p.get("type") == "popular" else ""}">'
        f'{PLACE_ICONS.get(p.get("type"), "📍")} {escape(p["name"])}</span>'
        for p in places
    )
    html(f'<div class="chips">{chips}</div>')
    source(f"Source: {activities.get('source', '-')}")


def itinerary_timeline(itinerary: list, trip: dict):
    if not itinerary:
        return
    dates = trip_dates(trip)
    blocks = ""
    for day in itinerary:
        when = ""
        if dates:
            when = f"{dates[0] + timedelta(days=day['day'] - 1):%A, %d %B}"
        blocks += (
            '<div class="day">'
            f'<div class="day-n">{day["day"]}</div>'
            f'<div class="day-card"><div class="day-meta">{when or "Day " + str(day["day"])}</div>'
            f'<div class="day-title">{escape(day["title"])}</div>'
            f'<div class="day-plan">{escape(day["plan"])}</div></div>'
            '</div>'
        )
    html(f'<div class="timeline">{blocks}</div>')


def callout(text: str, kind: str = ""):
    html(f'<div class="callout {kind}">{escape(text)}</div>')


def trip_notes(result: dict):
    notes = [
        "Rainy days are planned around indoor places where possible.",
        "Fares and hotel prices are estimates. Confirm before booking.",
    ]
    notes += result.get("warnings") or []
    notes += result.get("errors") or []
    items = "".join(f"<li>{escape(n)}</li>" for n in notes)
    html(f'<div class="panel pad"><div class="k-label">Good to know</div><ul class="tips">{items}</ul></div>')


def footer():
    html('<div class="foot"><span><b>TripMate</b> · Plan smarter trips across India</span>'
         '<span>Weather data by Open-Meteo.com. Maps and places © OpenStreetMap contributors. '
         'All prices are estimates.</span></div>')
