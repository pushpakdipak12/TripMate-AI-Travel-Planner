import json

from mcp_servers.geo import geocode, road_distance_km
from mcp_servers.providers.hotels import find_hotels
from mcp_servers.providers.places import find_attractions
from mcp_servers.providers.transport import compare_transport
from mcp_servers.providers.weather import get_forecast


def show(title, data):
    print("=" * 60)
    print(title)
    print(json.dumps(data, indent=2, ensure_ascii=False))


show("Geocode Pune", geocode("Pune"))
show("Road distance Pune -> Goa (km)", road_distance_km("Pune", "Goa"))
show("Weather Goa", get_forecast("Goa", 5))
show("Attractions Jaipur", find_attractions("Jaipur", 8))
show("Hotels Manali", find_hotels("Manali", nights=3, travelers=2, style="budget"))
show("Transport Pune -> Goa, 2 people", compare_transport("Pune", "Goa", 2))
show("Transport Mumbai -> Delhi, 3 people", compare_transport("Mumbai", "Delhi", 3))
