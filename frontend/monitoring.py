from html import escape

import streamlit as st

import api_client
import components as ui


def _seconds(ms) -> str:
    return f"{ms / 1000:.1f} s" if ms is not None else "–"


def monitoring_page():
    ui.brand(api_client.health())
    st.button("Refresh", key="refresh_stats")
    stats = api_client.stats()
    if not stats:
        ui.callout("The planner is offline. Start the backend with: uvicorn backend.main:app", "warn")
        return

    plan_latency = stats["endpoints"].get("/plan", {})
    cache = stats.get("cache", {})
    ratio = cache.get("hit_ratio")
    total_plans = sum(sum(v.values()) for v in stats["plans"].values())
    ui.html(
        '<div class="strip">'
        f'<div><div class="k-label">Plans created</div><div class="k-value big num">{total_plans}</div>'
        f'<div class="k-sub">{stats["requests"]} requests, {stats["errors"]} server errors</div></div>'
        f'<div><div class="k-label">Average plan time</div><div class="k-value big num">{_seconds(plan_latency.get("avg_ms"))}</div>'
        f'<div class="k-sub">p95 {_seconds(plan_latency.get("p95_ms"))}</div></div>'
        f'<div><div class="k-label">Cache hit ratio</div><div class="k-value big num">{f"{ratio:.0%}" if ratio is not None else "–"}</div>'
        f'<div class="k-sub">{cache.get("hits", 0)} hits, {cache.get("misses", 0)} misses</div></div>'
        f'<div><div class="k-label">Model</div><div class="k-value">{escape(stats.get("model", "-"))}</div>'
        f'<div class="k-sub">Backup model used {stats.get("llm_fallbacks", 0)} times, '
        f'up for {stats["uptime_seconds"] // 60} min</div></div>'
        '</div>'
    )

    left, right = st.columns([3, 2], gap="large")
    with left:
        ui.section("Time spent in each agent")
        rows = "".join(
            f'<tr><td class="opt">{escape(name)}</td><td class="r num">{s["count"]}</td>'
            f'<td class="r num">{_seconds(s["avg_ms"])}</td><td class="r num">{_seconds(s["p95_ms"])}</td>'
            f'<td class="r num">{_seconds(s["max_ms"])}</td></tr>'
            for name, s in sorted(stats["agents"].items(), key=lambda item: -item[1]["avg_ms"])
        ) or '<tr><td colspan="5" class="note">No plans yet. Create a plan to see agent timings.</td></tr>'
        ui.html('<div class="panel"><table class="data"><thead><tr><th>Agent</th><th class="r">Runs</th>'
                '<th class="r">Average</th><th class="r">p95</th><th class="r">Slowest</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')
        ui.source("Parallel agents (transport, hotels, weather, places) run at the same time, "
                  "so total plan time is close to the slowest of them, not the sum.")
    with right:
        ui.section("Plans by tab")
        rows = "".join(
            f'<tr><td class="opt">{escape(mode)}</td>'
            + "".join(f'<td class="r num">{outcomes.get(k, 0)}</td>' for k in ("ok", "clarification", "replan", "error"))
            + "</tr>"
            for mode, outcomes in stats["plans"].items()
        ) or '<tr><td colspan="5" class="note">No plans yet.</td></tr>'
        ui.html('<div class="panel"><table class="data"><thead><tr><th>Tab</th><th class="r">Done</th>'
                '<th class="r">Asked</th><th class="r">Replans</th><th class="r">Failed</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></div>')
        ui.section("Deeper tracing")
        ui.callout("Every plan is traced in LangSmith with its request ID: each agent, LLM call, prompt, "
                   "token count and cost. Raw Prometheus metrics are at /metrics on the backend.", "info")
