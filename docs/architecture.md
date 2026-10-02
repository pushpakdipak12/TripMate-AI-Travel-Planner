# Architecture

## Request flow (Full trip)

1. **Streamlit** sends `POST /plan` with `{mode, query}`.
2. **FastAPI middleware** creates a request ID, starts the timer and logs as JSON.
3. **Rate limiter** (Redis, fixed window per IP per minute) rejects floods with 429.
4. **Input guardrails** block prompt injection and long or empty queries, and mask phone numbers and emails.
5. **LangGraph** starts with a new `thread_id`. Each run is traced in LangSmith with the request ID.
6. **Query parser** (Groq, strict JSON schema into the `TripQuery` Pydantic model) fixes spelling,
   understands Hinglish and checks: India only (map lookup), trip limits, required fields.
   Missing info stops the graph with a question for the user.
7. **Mode router** reads the tab. Full trip fans out to four agents in parallel; a single tab
   runs one agent. No LLM decides the route.
8. **Agents call MCP tools**: weather (Open-Meteo), places and hotels (Overpass + curated list),
   transport (Nominatim + OSRM distance and a fare calculator). Results are cached in Redis.
9. **Transport agent**: Python calculates every option and fare; the LLM only picks one and explains why.
10. **Budget agent** (pure Python) adds everything up. Over budget: a conditional edge loops back to the
    hotel agent for a cheaper stay, at most twice, then adds saving tips.
11. **Itinerary agent** builds day plans from the real places list and the weather for each date.
12. **Output guardrails** recheck the total, the recommendation and the day count.
13. **Checkpointer** saves the state in Redis, so `POST /replan` can change transport and rerun
    only Budget and Itinerary.

## Where things live

| Folder | Role |
|---|---|
| `backend/api` | Routes, request and response models |
| `backend/graph` | State, router, graph builder, checkpointer, replan |
| `backend/agents` | One file per agent |
| `backend/prompts` | Prompts, separate from code |
| `backend/guardrails` | Input and output checks |
| `backend/cache` | Redis client and rate limiter |
| `backend/observability` | JSON logs, metrics, LangSmith run config |
| `mcp_servers` | MCP tool servers, providers, pricing rules, cache |
| `frontend` | Streamlit app, components, styles, Monitoring page |
| `tests` | Unit tests and evals |
