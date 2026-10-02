import sys

import requests

from mcp_servers.settings import USER_AGENT

# Main server is often busy, so we try mirrors one by one.
OVERPASS_URLS = [
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


def log(message: str):
    # MCP servers use stdout for messages, so logs must go to stderr.
    print(message, file=sys.stderr)


def overpass_search(query: str, timeout: int = 30) -> list:
    """Runs an Overpass query on each mirror until one works. Returns [] if all fail."""
    for url in OVERPASS_URLS:
        try:
            response = requests.post(
                url,
                data={"data": query},
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("remark"):
                # Overpass hides errors like "Query timed out" here, with status 200.
                log(f"Overpass {url} remark: {data['remark']}")
            elements = data.get("elements", [])
            if elements:
                return elements
            log(f"Overpass {url}: no results")
        except (requests.RequestException, ValueError) as e:
            log(f"Overpass {url} failed: {e}")
    return []


def famous_first(elements: list) -> list:
    """Places with a Wikipedia/Wikidata link are usually better known."""
    return sorted(elements, key=lambda e: "wikidata" not in e.get("tags", {}))
