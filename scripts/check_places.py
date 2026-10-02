import json

from mcp_servers.providers.places import find_attractions

for city in ["Goa", "Jaipur", "Udaipur"]:
    print("=" * 60)
    print(json.dumps(find_attractions(city, 8), indent=2, ensure_ascii=False))
