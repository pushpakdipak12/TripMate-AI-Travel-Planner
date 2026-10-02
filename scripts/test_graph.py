import asyncio
import uuid

from backend.graph.builder import close_graph, get_graph
from backend.graph.replan import replan


async def run(mode: str, query: str) -> tuple[str, dict]:
    graph = await get_graph()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    state = await graph.ainvoke({"mode": mode, "query": query, "retries": 0, "errors": []}, config)
    return thread_id, state


def show(title: str, state: dict):
    print("=" * 60)
    print(title)
    if state.get("needs_clarification"):
        print("ASK USER:", state["question"])
        return
    if state.get("transport", {}).get("options"):
        for o in state["transport"]["options"]:
            print(f"  {o['name']:<24} {o['duration_hours']:>5} hrs   ₹{o['price_min']:,} - ₹{o['price_max']:,}")
    if state.get("recommended_transport"):
        print("Recommended:", state["recommended_transport"])
    if state.get("chosen_hotel"):
        print("Hotel:", state["chosen_hotel"])
    if state.get("weather", {}).get("forecast"):
        for d in state["weather"]["forecast"]:
            print(f"  {d['date']}: {d['condition']}, {d['max_temp_c']}°C, rain {d['rain_chance_pct']}%")
    if state.get("activities", {}).get("places"):
        print("Places:", [p["name"] for p in state["activities"]["places"]])
    if state.get("budget"):
        print("Budget:", state["budget"])
        print("Retries:", state.get("retries"))
    for day in state.get("itinerary") or []:
        print(f"  Day {day['day']}: {day['title']} - {day['plan']}")
    if state.get("errors"):
        print("Errors:", state["errors"])


async def main():
    thread_id, state = await run("full_trip", "Pune to Goa, 5 days, 2 people, ₹60,000, beaches and seafood")
    show("FULL TRIP", state)

    state = await replan(thread_id, "Flight")
    show("REPLAN WITH FLIGHT (only budget + itinerary rerun)", state)

    _, state = await run("transport", "Mumbai to Jaipur, 4 people")
    show("TRANSPORT ONLY", state)

    _, state = await run("weather", "weather in munnar next 3 days")
    show("WEATHER ONLY", state)

    _, state = await run("budget", "3 days Udaipur from Pune, 2 people, ₹20,000")
    show("BUDGET (small budget, should retry with cheaper hotel)", state)

    _, state = await run("full_trip", "trip to jaipur for 3 days")
    show("MISSING ORIGIN", state)

    _, state = await run("full_trip", "Pune to Goa for 45 days")
    show("TOO LONG (trip limit guardrail)", state)

    await close_graph()


asyncio.run(main())
