import json
from pathlib import Path

from mcp_servers.cache import ONE_DAY, ONE_HOUR, cached
from mcp_servers.geo import geocode
from mcp_servers.providers.osm import famous_first, overpass_search

# Famous places for popular destinations. Shown first so the highlights are
# always there, and used alone when OpenStreetMap is slow.
POPULAR_FILE = Path(__file__).resolve().parents[2] / "data" / "popular_places.json"
POPULAR_PLACES = json.loads(POPULAR_FILE.read_text(encoding="utf-8"))
MAX_POPULAR = 6


@cached("osm_places", 7 * ONE_DAY, empty_ttl_seconds=ONE_HOUR)
def from_openstreetmap(city: str, limit: int) -> list[dict]:
    coords = geocode(city)
    if not coords:
        return []
    lat, lon = coords
    query = f"""
    [out:json][timeout:25];
    (
      nwr["tourism"~"attraction|museum|viewpoint"]["name"](around:15000,{lat},{lon});
      nwr["natural"="beach"]["name"](around:15000,{lat},{lon});
      nwr["historic"~"fort|monument|castle|palace"]["name"](around:15000,{lat},{lon});
    );
    out center 80;
    """
    places, seen = [], set()
    for element in famous_first(overpass_search(query, timeout=30)):
        tags = element.get("tags", {})
        name = tags.get("name:en") or tags.get("name")
        if not name or name in seen:
            continue
        seen.add(name)
        place_type = tags.get("tourism") or tags.get("historic") or tags.get("natural")
        places.append({"name": name, "type": place_type})
        if len(places) >= limit:
            break
    return places


def find_attractions(city: str, limit: int = 10) -> dict:
    popular = [{"name": n, "type": "popular"} for n in POPULAR_PLACES.get(city.strip().lower(), [])[:MAX_POPULAR]]
    osm = from_openstreetmap(city, limit)

    places, seen = [], set()
    for place in popular + osm:
        if place["name"].lower() not in seen:
            seen.add(place["name"].lower())
            places.append(place)
    places = places[:limit]

    if not places:
        return {"city": city, "places": [], "note": "No places found right now. Try again later."}
    sources = [name for name, items in (("Popular places", popular), ("OpenStreetMap", osm)) if items]
    return {"city": city, "source": " + ".join(sources), "places": places}
