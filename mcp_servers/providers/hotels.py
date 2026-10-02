import math
import zlib

from mcp_servers.cache import ONE_DAY, ONE_HOUR, cached
from mcp_servers.geo import geocode
from mcp_servers.pricing.rates import HOTEL_PER_NIGHT, PREMIUM_CITIES, PREMIUM_MULTIPLIER
from mcp_servers.providers.osm import overpass_search

SAMPLE_NAMES = {
    "budget": ["Budget Inn", "Guest House", "Backpackers Hostel"],
    "mid": ["Residency", "Comfort Stay", "Grand Hotel"],
    "luxury": ["Palace Resort", "Royal Retreat", "Grand Luxury Hotel"],
}


def hotel_category(tags: dict) -> str:
    """Guess budget / mid / luxury from OpenStreetMap tags."""
    stars = tags.get("stars", "")
    if stars[:1].isdigit():
        number = int(stars[0])
        if number >= 5:
            return "luxury"
        if number >= 3:
            return "mid"
        return "budget"
    if tags.get("tourism") in ("hostel", "guest_house"):
        return "budget"
    if "wikidata" in tags:
        return "luxury"     # famous hotels are usually high-end
    return "mid"


def estimate_price(hotel_name: str, city: str, style: str) -> int:
    """Same hotel always gets the same price (stable demo)."""
    low, high = HOTEL_PER_NIGHT[style]
    if city.strip().lower() in PREMIUM_CITIES:
        low, high = low * PREMIUM_MULTIPLIER, high * PREMIUM_MULTIPLIER
    position = zlib.crc32(hotel_name.encode()) % 100 / 100
    return int(round((low + (high - low) * position) / 100) * 100)


@cached("osm_hotels", 7 * ONE_DAY, empty_ttl_seconds=ONE_HOUR)
def get_osm_hotels(city: str) -> list[dict]:
    coords = geocode(city)
    if not coords:
        return []
    lat, lon = coords
    query = f"""
    [out:json][timeout:25];
    nwr["tourism"~"hotel|guest_house|hostel"]["name"](around:8000,{lat},{lon});
    out center 80;
    """
    hotels, seen = [], set()
    for element in overpass_search(query, timeout=30):
        tags = element.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if name and name not in seen:
            seen.add(name)
            hotels.append({"name": name, "category": hotel_category(tags)})
    return hotels


def find_hotels(city: str, nights: int = 1, travelers: int = 1, style: str = "mid", limit: int = 5) -> dict:
    style = style if style in HOTEL_PER_NIGHT else "mid"
    matching = [h for h in get_osm_hotels(city) if h["category"] == style][:limit]
    source = "Names from OpenStreetMap, prices estimated"

    if len(matching) < 3:
        samples = [{"name": f"{city} {name}", "category": style} for name in SAMPLE_NAMES[style]]
        matching += samples[: 3 - len(matching)]
        source = "OpenStreetMap + sample hotels, prices estimated"

    rooms = math.ceil(travelers / 2)
    hotels = []
    for hotel in matching:
        per_night = estimate_price(hotel["name"], city, style)
        hotels.append({
            "name": hotel["name"],
            "category": style,
            "price_per_room_night": per_night,
            "rooms": rooms,
            "total_price": per_night * rooms * nights,
        })
    hotels.sort(key=lambda h: h["price_per_room_night"])
    return {"city": city, "nights": nights, "style": style, "source": source, "hotels": hotels}
