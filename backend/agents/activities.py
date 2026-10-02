from backend.llm.provider import get_structured_llm
from backend.models.plan import PlaceList
from backend.prompts.places_prompt import places_prompt
from backend.tools.mcp_client import call_tool


async def suggest_with_llm(city: str) -> dict:
    """Last fallback when the map and our curated list have nothing."""
    chain = places_prompt | get_structured_llm(PlaceList)
    result = await chain.ainvoke({"city": city})
    places = [{"name": name, "type": "suggested"} for name in result.places[:8]]
    return {"city": city, "source": "AI suggestions (please verify)", "places": places}


async def activities_agent(state: dict) -> dict:
    city = state["trip"]["destination"]
    result = await call_tool("search_attractions", {"city": city, "limit": 10})
    if result.get("places"):
        return {"activities": result}

    try:
        result = await suggest_with_llm(city)
    except Exception as e:
        return {"activities": result, "errors": [f"Activities: {e}"]}
    if not result["places"]:
        return {"activities": result, "errors": ["Activities: no places found"]}
    return {"activities": result}
