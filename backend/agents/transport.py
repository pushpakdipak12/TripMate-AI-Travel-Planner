from backend.llm.provider import get_structured_llm
from backend.models.plan import TransportChoice
from backend.prompts.transport_prompt import transport_prompt
from backend.tools.mcp_client import call_tool


async def transport_agent(state: dict) -> dict:
    trip = state["trip"]
    result = await call_tool("compare_transport_options", {
        "origin": trip["origin"],
        "destination": trip["destination"],
        "travelers": trip["travelers"],
    })
    if "error" in result or not result.get("options"):
        return {"transport": result, "errors": [f"Transport: {result.get('error', 'no options')}"]}

    # Python found the options and prices. The LLM only picks one and explains why.
    chain = transport_prompt | get_structured_llm(TransportChoice)
    choice = await chain.ainvoke({"trip": trip, "options": result["options"]})

    names = [option["name"] for option in result["options"]]
    if choice.option_name not in names:
        cheapest = min(result["options"], key=lambda o: o["price_min"])
        choice = TransportChoice(option_name=cheapest["name"], reason="Cheapest available option.")

    return {"transport": result, "recommended_transport": choice.model_dump()}
