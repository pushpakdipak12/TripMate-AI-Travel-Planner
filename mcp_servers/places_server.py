from mcp.server.fastmcp import FastMCP

from mcp_servers.providers.hotels import find_hotels
from mcp_servers.providers.places import find_attractions

mcp = FastMCP("places")


@mcp.tool()
def search_attractions(city: str, limit: int = 10) -> dict:
    """Tourist places in an Indian city: forts, beaches, museums, viewpoints."""
    return find_attractions(city, limit)


@mcp.tool()
def search_hotels(city: str, nights: int = 1, travelers: int = 1, style: str = "mid") -> dict:
    """Hotels in an Indian city with estimated prices. style: budget, mid or luxury."""
    return find_hotels(city, nights, travelers, style)


if __name__ == "__main__":
    mcp.run()
