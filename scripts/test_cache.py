import time

from mcp_servers.geo import geocode, road_distance_km
from mcp_servers.providers.places import find_attractions
from mcp_servers.providers.weather import get_forecast


def timed(label, func, *args):
    start = time.time()
    result = func(*args)
    print(f"{label:<28} {time.time() - start:6.2f} s")
    return result


for attempt in ("1st call (API)", "2nd call (Redis)"):
    print("=" * 45, attempt)
    timed("geocode Udaipur", geocode, "Udaipur")
    timed("distance Pune -> Udaipur", road_distance_km, "Pune", "Udaipur")
    timed("weather Udaipur", get_forecast, "Udaipur", 5)
    places = timed("attractions Udaipur", find_attractions, "Udaipur", 8)

print("\nPlaces:", [p["name"] for p in places["places"]])
print("Source:", places.get("source"))
