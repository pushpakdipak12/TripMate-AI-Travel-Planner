import asyncio

from backend.tools.mcp_client import get_mcp_tools


async def main():
    tools = await get_mcp_tools()
    print("Tools found through MCP:")
    for tool in tools:
        print(" -", tool.name)

    tools_by_name = {tool.name: tool for tool in tools}

    print("\nweather_forecast(Goa):")
    print(await tools_by_name["weather_forecast"].ainvoke({"city": "Goa", "days": 3}))

    print("\ncompare_transport_options(Pune -> Goa, 2 people):")
    print(await tools_by_name["compare_transport_options"].ainvoke(
        {"origin": "Pune", "destination": "Goa", "travelers": 2}
    ))


asyncio.run(main())
