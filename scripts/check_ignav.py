import json
from datetime import date, timedelta

import requests

from mcp_servers.settings import IGNAV_API_KEY

if not IGNAV_API_KEY:
    raise SystemExit("Add IGNAV_API_KEY to .env first")

response = requests.post(
    "https://ignav.com/api/fares/one-way",
    headers={"X-Api-Key": IGNAV_API_KEY, "Content-Type": "application/json"},
    json={
        "origin": "PNQ",
        "destination": "GOI",
        "departure_date": (date.today() + timedelta(days=30)).isoformat(),
    },
    timeout=60,
)
print("Status:", response.status_code)
print(json.dumps(response.json(), indent=2)[:3000])
