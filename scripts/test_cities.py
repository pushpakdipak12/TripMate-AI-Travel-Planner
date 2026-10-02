import asyncio

from backend.graph.builder import close_graph, get_graph

# Different sizes and regions of India, including spelling mistakes.
TRIPS = [
    "Pune to Varanasi, 4 days, 2 people, budget ₹40,000",
    "pune to varanaci 3 days 2 people",
    "Delhi to Hampi, 4 days, 2 people",
    "Chennai to Ooty, 3 days, 4 people",
    "Kolkata to Shillong, 5 days, 2 people",
    "Bengaluru to Kanyakumari, 3 days, 1 person",
    "Ahmedabad to Bhuj, 2 days, 3 people",
    "Nagpur to Pachmarhi, 3 days, 2 people",
]


async def main():
    graph = await get_graph()
    for number, query in enumerate(TRIPS):
        config = {"configurable": {"thread_id": f"city-test-{number}"}}
        state = await graph.ainvoke({"mode": "full_trip", "query": query, "retries": 0, "errors": []}, config)
        print("=" * 60)
        print(query)
        if state.get("needs_clarification"):
            print("  ASK USER:", state["question"])
            continue
        trip = state["trip"]
        options = [o["name"] for o in state.get("transport", {}).get("options", [])]
        print(f"  Parsed     : {trip['origin']} -> {trip['destination']}, {trip['days']} days")
        print(f"  Transport  : {options}")
        print(f"  Recommended: {state.get('recommended_transport', {}).get('option_name')}")
        print(f"  Hotel      : {state.get('chosen_hotel', {}).get('name')}")
        print(f"  Weather    : {len(state.get('weather', {}).get('forecast', []))} days")
        places = state.get("activities", {})
        print(f"  Places     : {[p['name'] for p in places.get('places', [])][:5]} ({places.get('source')})")
        print(f"  Budget     : ₹{state.get('budget', {}).get('total', 0):,}")
        print(f"  Itinerary  : {len(state.get('itinerary') or [])} days")
        if state.get("errors"):
            print("  ERRORS     :", state["errors"])
    await close_graph()


asyncio.run(main())
