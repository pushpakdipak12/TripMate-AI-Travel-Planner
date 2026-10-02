from datetime import date, timedelta

import requests

from mcp_servers.cache import ONE_HOUR, cached
from mcp_servers.geo import geocode
from mcp_servers.settings import HTTP_TIMEOUT

MAX_FORECAST_DAYS = 16      # Open-Meteo forecasts only 16 days ahead

WEATHER_CODES = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Cloudy",
    45: "Fog", 48: "Fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    80: "Rain showers", 81: "Rain showers", 82: "Heavy showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def forecast_dates(days: int, start_date: str | None):
    """Returns (first_day, last_day), or None if the trip is outside the forecast window."""
    today = date.today()
    last_allowed = today + timedelta(days=MAX_FORECAST_DAYS - 1)
    first = date.fromisoformat(start_date) if start_date else today
    if first < today or first > last_allowed:
        return None
    last = min(first + timedelta(days=max(1, days) - 1), last_allowed)
    return first, last


@cached("weather", ONE_HOUR, should_cache=lambda result: "error" not in result)
def get_forecast(city: str, days: int = 5, start_date: str | None = None) -> dict:
    coords = geocode(city)
    if not coords:
        return {"city": city, "error": "City not found"}

    try:
        window = forecast_dates(days, start_date)
    except ValueError:
        return {"city": city, "error": f"Invalid date: {start_date}"}
    if window is None:
        return {
            "city": city,
            "forecast": [],
            "note": f"Forecast is only available for the next {MAX_FORECAST_DAYS} days. Check again closer to your trip.",
        }

    params = {
        "latitude": coords[0],
        "longitude": coords[1],
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "Asia/Kolkata",
        "start_date": window[0].isoformat(),
        "end_date": window[1].isoformat(),
    }
    try:
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        daily = response.json()["daily"]
    except (requests.RequestException, KeyError):
        return {"city": city, "error": "Weather service unavailable"}

    forecast = []
    for i, day in enumerate(daily["time"]):
        forecast.append({
            "date": day,
            "condition": WEATHER_CODES.get(daily["weather_code"][i], "Unknown"),
            "max_temp_c": daily["temperature_2m_max"][i],
            "min_temp_c": daily["temperature_2m_min"][i],
            "rain_chance_pct": daily["precipitation_probability_max"][i],
        })
    return {"city": city, "source": "Weather data by Open-Meteo.com", "forecast": forecast}
