import json
from pathlib import Path

from mcp_servers.geo import geocode

CITIES_FILE = Path(__file__).resolve().parents[2] / "data" / "indian_cities.json"
INDIAN_CITIES = set(json.loads(CITIES_FILE.read_text(encoding="utf-8")))


def is_indian_place(name: str) -> bool:
    """Fast check with our list, then a real map lookup limited to India."""
    city = name.split(",")[0].strip().lower()
    if city in INDIAN_CITIES:
        return True
    return geocode(city) is not None
