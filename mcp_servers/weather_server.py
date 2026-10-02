from mcp.server.fastmcp import FastMCP

from mcp_servers.providers.weather import get_forecast

mcp = FastMCP("weather")


@mcp.tool()
def weather_forecast(city: str, days: int = 5, start_date: str | None = None) -> dict:
    """Daily weather for an Indian city. start_date is YYYY-MM-DD (default today). Max 16 days ahead."""
    return get_forecast(city, days, start_date)


if __name__ == "__main__":
    mcp.run()
