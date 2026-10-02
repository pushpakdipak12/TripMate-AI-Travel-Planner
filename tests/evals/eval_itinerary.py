"""
Itinerary quality with LLM-as-judge. Runs real trips through the full graph,
then a judge LLM scores each itinerary from 1 to 5.

    python -m tests.evals.eval_itinerary
"""
import asyncio
import uuid

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.graph.builder import close_graph, get_graph
from backend.llm.provider import get_structured_llm

TRIPS = [
    "Pune to Goa, 4 days, 2 people, budget ₹40,000, beaches and seafood",
    "Delhi to Jaipur, 3 days, 2 people, forts and food",
    "Mumbai to Munnar, 4 days, 2 people, nature and tea gardens",
]


class JudgeScore(BaseModel):
    uses_given_places: int = Field(description="1-5: uses only places from the given list")
    weather_aware: int = Field(description="1-5: indoor plans on rainy days, outdoor on clear days")
    matches_interests: int = Field(description="1-5: fits the traveller's interests")
    variety: int = Field(description="1-5: no repeated places, good mix across days")
    comment: str = Field(description="One sentence on the biggest problem, or 'Good'")


judge_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict travel plan reviewer. Score each criterion from 1 (bad) to 5 (excellent).\n"
               "The product's weather rule: outdoor places should go on the days with the lowest chance of rain, "
               "and rainy days should favour indoor places. If every day is rainy, it is correct to still include "
               "each main interest once, on the least rainy day, marked 'weather permitting'. Score weather_aware "
               "against this rule: penalise outdoor plans on rainy days when a drier day was available."),
    ("human", "Interests: {interests}\nAllowed places: {places}\nWeather by day: {weather}\n\nItinerary:\n{itinerary}"),
])


async def main():
    graph = await get_graph()
    judge = judge_prompt | get_structured_llm(JudgeScore)
    averages = []
    for query in TRIPS:
        config = {"configurable": {"thread_id": f"eval-{uuid.uuid4()}"}, "run_name": "eval_itinerary"}
        state = await graph.ainvoke({"mode": "full_trip", "query": query, "retries": 0, "errors": []}, config)
        if not state.get("itinerary"):
            print(f"SKIP  {query} (no itinerary: {state.get('question') or state.get('errors')})")
            continue
        score = await judge.ainvoke({
            "interests": state["trip"].get("interests"),
            "places": [p["name"] for p in state.get("activities", {}).get("places", [])],
            "weather": [f"{d['date']}: {d['condition']}, rain {d['rain_chance_pct']}%"
                        for d in state.get("weather", {}).get("forecast", [])] or "Not available",
            "itinerary": "\n".join(f"Day {d['day']}: {d['title']} - {d['plan']}" for d in state["itinerary"]),
        })
        values = [score.uses_given_places, score.weather_aware, score.matches_interests, score.variety]
        averages.append(sum(values) / len(values))
        print(f"{averages[-1]:.1f}/5  {query}")
        print(f"       places {score.uses_given_places}, weather {score.weather_aware}, "
              f"interests {score.matches_interests}, variety {score.variety}. {score.comment}")
    if averages:
        print("=" * 60)
        print(f"Average itinerary score: {sum(averages) / len(averages):.1f} / 5")
    await close_graph()


asyncio.run(main())
