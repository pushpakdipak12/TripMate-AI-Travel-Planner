from mcp.server.fastmcp import FastMCP

from mcp_servers.providers.transport import compare_transport

mcp = FastMCP("transport")


@mcp.tool()
def compare_transport_options(origin: str, destination: str, travelers: int = 1) -> dict:
    """Compares flight, train, bus, cab and self-drive between two Indian cities with estimated prices."""
    return compare_transport(origin, destination, travelers)


if __name__ == "__main__":
    mcp.run()
