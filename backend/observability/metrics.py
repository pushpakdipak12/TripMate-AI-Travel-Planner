import statistics
import time
from collections import defaultdict, deque

from prometheus_client import Counter, Histogram

# ---------- Prometheus metrics (scraped from /metrics) ----------
REQUESTS = Counter("tripmate_http_requests_total", "HTTP requests", ["path", "status"])
REQUEST_LATENCY = Histogram("tripmate_http_request_seconds", "HTTP request latency", ["path"],
                            buckets=(0.1, 0.5, 1, 2, 5, 10, 20, 40, 60, 120))
PLANS = Counter("tripmate_plans_total", "Plans created", ["mode", "outcome"])
LLM_FALLBACKS = Counter("tripmate_llm_fallbacks_total", "Times the backup model (Ollama) answered")
NODE_LATENCY = Histogram("tripmate_agent_seconds", "Time spent in each agent", ["agent"],
                         buckets=(0.01, 0.1, 0.5, 1, 2, 5, 10, 20, 40, 60))

# ---------- Small in-memory copy for the Monitoring page ----------
_samples = defaultdict(lambda: deque(maxlen=500))
_counts = defaultdict(int)
STARTED_AT = time.time()


def record_request(path: str, status: int, seconds: float):
    REQUESTS.labels(path, str(status)).inc()
    REQUEST_LATENCY.labels(path).observe(seconds)
    _samples[("request", path)].append(seconds)
    _counts["requests"] += 1
    if status >= 500:
        _counts["errors"] += 1


def record_plan(mode: str, outcome: str):
    PLANS.labels(mode, outcome).inc()
    _counts[f"plan:{mode}:{outcome}"] += 1


def record_fallback():
    LLM_FALLBACKS.inc()
    _counts["llm_fallbacks"] += 1


def record_node(agent: str, seconds: float):
    NODE_LATENCY.labels(agent).observe(seconds)
    _samples[("agent", agent)].append(seconds)


def _summary(values) -> dict:
    values = sorted(values)
    p95 = values[min(len(values) - 1, int(len(values) * 0.95))]
    return {"count": len(values), "avg_ms": round(statistics.mean(values) * 1000),
            "p95_ms": round(p95 * 1000), "max_ms": round(values[-1] * 1000)}


def snapshot() -> dict:
    plans = defaultdict(dict)
    for key, value in _counts.items():
        if key.startswith("plan:"):
            _, mode, outcome = key.split(":")
            plans[mode][outcome] = value
    return {
        "uptime_seconds": round(time.time() - STARTED_AT),
        "requests": _counts["requests"],
        "errors": _counts["errors"],
        "llm_fallbacks": _counts["llm_fallbacks"],
        "plans": plans,
        "endpoints": {name: _summary(v) for (group, name), v in _samples.items() if group == "request" and v},
        "agents": {name: _summary(v) for (group, name), v in _samples.items() if group == "agent" and v},
    }
