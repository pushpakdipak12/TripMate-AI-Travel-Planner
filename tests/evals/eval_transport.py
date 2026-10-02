"""
Transport recommendation evaluation: does the LLM pick a sensible option?
Distances are fixed in the dataset, so only the LLM's choice is being tested.

    python -m tests.evals.eval_transport
"""
import asyncio
import json
from pathlib import Path

import mcp_servers.providers.transport as transport_provider
from backend.llm.provider import get_structured_llm
from backend.models.plan import TransportChoice
from backend.prompts.transport_prompt import transport_prompt

DATASET = json.loads((Path(__file__).parent / "transport_dataset.json").read_text(encoding="utf-8"))


async def main():
    chain = transport_prompt | get_structured_llm(TransportChoice)
    passed = 0
    for case in DATASET:
        transport_provider.road_distance_km = lambda a, b, km=case["distance_km"]: km
        trip = case["trip"]
        options = transport_provider.compare_transport(trip["origin"], trip["destination"], trip["travelers"])["options"]
        choice = await chain.ainvoke({"trip": trip, "options": options})
        ok = choice.option_name in case["allowed"]
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['name']:<40} -> {choice.option_name}")
        if not ok:
            print(f"      expected one of {case['allowed']}. Reason given: {choice.reason}")
    print("=" * 60)
    print(f"Sensible recommendations: {passed}/{len(DATASET)} = {passed / len(DATASET):.0%}")


asyncio.run(main())
