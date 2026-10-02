import json
import math
import time
from pathlib import Path

import requests

from mcp_servers.cache import ONE_DAY, cached
from mcp_servers.settings import HTTP_TIMEOUT, USER_AGENT

HEADERS = {"User-Agent": USER_AGENT}

# Regions like Goa are states. Nominatim returns the state's center (far from
# beaches), so we pin regions to their main tourist hub.
CENTERS_FILE = Path(__file__).resolve().parents[1] / "data" / "place_centers.json"
PLACE_CENTERS = json.loads(CENTERS_FILE.read_text(encoding="utf-8"))

_last_nominatim_call = 0.0


def _wait_one_second():
    """Nominatim allows max 1 request per second."""
    global _last_nominatim_call
    gap = time.time() - _last_nominatim_call
    if gap < 1:
        time.sleep(1 - gap)
    _last_nominatim_call = time.time()


@cached("geo", 30 * ONE_DAY, should_cache=lambda result: result is not None)
def _nominatim_lookup(city: str):
    _wait_one_second()
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": city, "countrycodes": "in", "featureType": "settlement", "format": "json", "limit": 1},
            headers=HEADERS,
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json()
    except requests.RequestException:
        return None
    if not results:
        return None
    return [float(results[0]["lat"]), float(results[0]["lon"])]


def geocode(city: str):
    """City name -> [lat, lon]. Returns None if not found."""
    key = city.strip().lower()
    if key in PLACE_CENTERS:
        return PLACE_CENTERS[key]
    return _nominatim_lookup(key)


def straight_line_km(a, b) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


@cached("distance", 30 * ONE_DAY, should_cache=lambda result: result is not None)
def road_distance_km(origin: str, destination: str):
    """Road distance from OSRM. Falls back to straight line x 1.3."""
    a, b = geocode(origin), geocode(destination)
    if not a or not b:
        return None

    url = f"https://router.project-osrm.org/route/v1/driving/{a[1]},{a[0]};{b[1]},{b[0]}"
    try:
        response = requests.get(url, params={"overview": "false"}, headers=HEADERS, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        return response.json()["routes"][0]["distance"] / 1000
    except (requests.RequestException, KeyError, IndexError):
        return straight_line_km(a, b) * 1.3
