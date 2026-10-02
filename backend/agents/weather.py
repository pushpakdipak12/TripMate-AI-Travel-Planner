from backend.tools.mcp_client import call_tool


async def weather_agent(state: dict) -> dict:
    trip = state["trip"]
    result = await call_tool("weather_forecast", {
        "city": trip["destination"],
        "days": trip.get("days") or 5,
        "start_date": trip.get("start_date"),
    })
    if "error" in result:
        return {"weather": result, "errors": [f"Weather: {result['error']}"]}
    return {"weather": result}
