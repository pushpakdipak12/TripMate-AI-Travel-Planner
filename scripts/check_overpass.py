import requests

from mcp_servers.providers.osm import OVERPASS_URLS
from mcp_servers.settings import USER_AGENT

QUERY = """
[out:json][timeout:25];
nwr["tourism"="hotel"]["name"](around:3000,18.52,73.85);
out center 5;
"""

for url in OVERPASS_URLS:
    print("=" * 60)
    print(url)
    try:
        response = requests.post(url, data={"data": QUERY}, headers={"User-Agent": USER_AGENT}, timeout=45)
        print("Status:", response.status_code)
        if response.ok:
            elements = response.json().get("elements", [])
            print("Hotels found:", len(elements))
            for e in elements:
                print(" -", e.get("tags", {}).get("name"))
        else:
            print(response.text[:300])
    except Exception as e:
        print("Error:", e)
