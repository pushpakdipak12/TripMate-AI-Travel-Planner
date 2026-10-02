from backend.agents.query_parser import parse_query

TEST_CASES = [
    ("full_trip", "Pune to Goa, 5 days, 2 people, ₹60,000, beaches and seafood"),
    ("full_trip", "pune se goa 5 din 2 log 60k budget"),
    ("transport", "Mumbai to Delhi on 15 December, 3 people"),
    ("hotels", "cheap hotels in manali for 3 nights"),
    ("weather", "weather in munnar next week"),
    ("full_trip", "trip to jaipur for 3 days"),
    ("full_trip", "Paris to London, 4 days"),
]

for mode, query in TEST_CASES:
    result = parse_query(query, mode)
    print("=" * 60)
    print(f"[{mode}] {query}")
    print(result.trip.model_dump())
    if result.needs_clarification:
        print("ASK USER:", result.question)
    else:
        print("OK")
