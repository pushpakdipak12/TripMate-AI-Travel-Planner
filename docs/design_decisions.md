# Design decisions

**Tabs decide the route, not the LLM.** An early version let an LLM choose which agents to run,
and it sometimes chose wrong. The user already knows what they want, so the tab sets the mode and a
plain Python router picks the agents. Routing is now 100% predictable and testable.

**LLM for language, Python for numbers.** Fares, hotel prices and budgets are calculated in Python.
The LLM understands queries, recommends and writes the itinerary, but never invents a price.
This removed price hallucinations and made the budget unit-testable.

**Strict JSON schema output.** Tool-calling based structured output occasionally returned broken JSON.
Groq's strict JSON schema mode constrains generation to the Pydantic schema, plus retries and an Ollama
fallback for availability.

**LangGraph over plain chains, CrewAI or AutoGen.** The workflow needs parallel branches, a conditional
loop (budget retry), stopping for clarification and checkpointed state for replanning. LangGraph gives
explicit control over each of these.

**MCP servers for tools.** Data sources sit behind MCP servers, so agents do not know whether data is
live, cached or curated. A paid provider can replace a free one without touching agent code.

**Redis for three jobs.** API cache (geocoding 30 days, places 7 days, weather 1 hour), per-user rate
limiting and the LangGraph checkpointer. Each falls back gracefully: no Redis means no cache, and plans
are saved in a local SQLite file instead.

**Partial rerun on replan.** Changing transport loads the saved state and reruns only Budget and
Itinerary, about a second instead of a full minute.

**Layered fallbacks for places.** OpenStreetMap, then a curated list of famous places, then clearly
labelled AI suggestions. Demos never show an empty section.

**Honest estimates.** Every price is labelled as an estimate, data sources are credited, and the
16-day forecast limit is explained to the user instead of showing misleading weather.

## Scaling to 10,000 users

Run several API containers behind a load balancer; they are stateless because state lives in Redis.
Move MCP servers to HTTP transport as separate services so they scale on their own. Increase Redis
memory, put popular routes in a warm cache, and switch to paid map and weather providers with SLAs.
Add per-user API keys or OAuth instead of IP rate limits, and alert on p95 latency and error rate
from the Prometheus metrics.
