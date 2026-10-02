import asyncio
import json
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient


def server(module: str) -> dict:
    return {"command": sys.executable, "args": ["-m", module], "transport": "stdio"}


MCP_SERVERS = {
    "weather": server("mcp_servers.weather_server"),
    "places": server("mcp_servers.places_server"),
    "transport": server("mcp_servers.transport_server"),
}

_tools = None
_lock = asyncio.Lock()


async def get_mcp_tools():
    client = MultiServerMCPClient(MCP_SERVERS)
    return await client.get_tools()


async def call_tool(name: str, args: dict) -> dict:
    """Calls an MCP tool by name and returns its result as a dict."""
    global _tools
    async with _lock:
        if _tools is None:
            _tools = {tool.name: tool for tool in await get_mcp_tools()}

    result = await _tools[name].ainvoke(args)
    text = result[0]["text"] if isinstance(result, list) else result
    return json.loads(text)
