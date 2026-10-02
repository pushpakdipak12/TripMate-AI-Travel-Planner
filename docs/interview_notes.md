# Interview notes

## 2-minute pitch

"I built TripMate, a multi-agent travel planner for India. A user types a trip like 'Pune to Goa,
5 days, 2 people, 60k', even in Hinglish, and gets transport options with fares, a hotel, the weather,
places to visit, a budget and a weather-aware itinerary.

It is a LangGraph workflow. A parser turns the text into a strict Pydantic schema. Based on the tab,
a router runs agents: for a full trip, transport, hotels, weather and places run in parallel, then a
budget agent checks the total and loops back for a cheaper hotel if needed, and an itinerary agent
writes the plan. Agents use tools through MCP servers backed by Open-Meteo and OpenStreetMap.

Two decisions mattered most. First, the LLM never calculates prices; Python does, so there are no
price hallucinations. Second, routing is deterministic by tab, which fixed a real bug where an LLM
router picked the wrong agents.

For production I added Redis for caching, rate limiting and checkpoints, guardrails for injection and
PII, LangSmith tracing, Prometheus metrics, evals including LLM-as-judge, unit tests and CI."

## Resume bullets (fill in your measured numbers)

- Built a multi-agent travel planner with LangGraph, MCP and Groq that plans full trips for any Indian
  city; parallel agents cut planning time from about __ s to __ s.
- Added Redis caching, rate limiting and checkpointing; cache hit ratio __%, repeat lookups from __ s
  to __ ms, and transport changes replan in about 1 s by rerunning only 2 of 7 agents.
- Reached __% field accuracy on a 20-case parser eval and __/5 itinerary quality with LLM-as-judge;
  added input/output guardrails, LangSmith tracing, Prometheus metrics and GitHub Actions CI.

Where to get the numbers: Monitoring page (agent times, cache ratio), `scripts/test_cache.py`,
`tests/evals/*`.

## Likely questions

1. **Why LangGraph?** Parallel branches, a conditional loop, stop-for-clarification and saved state.
2. **How do agents run in parallel?** The router returns a list of nodes; LangGraph runs them in one
   step and waits for all before Budget.
3. **How does the budget loop end?** A retry counter in state; at most 2 retries, then saving tips.
4. **Why not let the LLM route?** It misrouted in testing. Tabs make routing deterministic.
5. **How do you stop price hallucinations?** Prices only come from Python; output checks recompute totals.
6. **How do you get reliable JSON?** Strict JSON schema mode, Pydantic validation, retries, fallback model.
7. **What is MCP and why use it?** A standard protocol for tools; data sources can change without
   changing agents.
8. **What does Redis do?** Cache, rate limit, checkpointer. Each degrades gracefully.
9. **What is a checkpointer?** Saved graph state per thread, used for replanning and resuming.
10. **How does replan work?** Load state by thread ID, change transport, rerun Budget and Itinerary only.
11. **What guardrails exist?** Injection patterns, length limits, PII masking, India check, trip limits,
    output total check, recommendation check, day-count check.
12. **How do you trace a bad answer?** Find the request ID in logs, open the LangSmith trace, see each
    agent's input, output, prompt and tokens.
13. **What metrics matter?** p95 plan latency, per-agent time, error rate, cache hit ratio, plans per tab.
14. **How do you evaluate an LLM system?** Unit tests for code, field-accuracy evals for the parser,
    rule-based evals for recommendations, LLM-as-judge for itineraries.
15. **What is the latency bottleneck?** Slow public map servers on first lookup; solved by caching.
16. **What if Groq is down?** Retries, then Ollama answers.
17. **What if a map server is down?** Mirrors, then curated data, then labelled AI suggestions.
18. **How is the India check done?** Fast list, then a map lookup restricted to Indian settlements.
19. **How do you handle Hinglish and typos?** Few-shot examples and spelling rules in the parser prompt,
    measured by the eval set.
20. **Why Streamlit?** Fast to build a polished internal-style UI in Python; the API is separate,
    so a React UI could replace it.
21. **How would you scale it?** Stateless API replicas, MCP servers over HTTP, bigger Redis, paid data.
22. **What would you add next?** Live fares from a partner API, user accounts, booking links, multi-city trips.
23. **What did you learn?** Keep LLMs away from arithmetic, make routing deterministic when users
    already know intent, and measure everything.
24. **Biggest bug you fixed?** Broken JSON from tool calling, fixed with strict schema mode.
25. **How is cost controlled?** Small fast model, caching, rate limits, and token tracking in LangSmith.
