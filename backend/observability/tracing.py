import asyncio
import time
from functools import wraps

from backend.observability.logging import log_event
from backend.observability.metrics import record_node


def timed_node(name: str, func):
    """Wraps a LangGraph node: records how long each agent takes."""
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(state):
            start = time.perf_counter()
            try:
                return await func(state)
            finally:
                seconds = time.perf_counter() - start
                record_node(name, seconds)
                log_event("agent finished", agent=name, ms=round(seconds * 1000))
        return async_wrapper

    @wraps(func)
    def sync_wrapper(state):
        start = time.perf_counter()
        try:
            return func(state)
        finally:
            seconds = time.perf_counter() - start
            record_node(name, seconds)
            log_event("agent finished", agent=name, ms=round(seconds * 1000))
    return sync_wrapper


def run_config(thread_id: str, mode: str, request_id: str) -> dict:
    """LangGraph config: thread for the checkpointer, plus names and tags for LangSmith."""
    return {
        "configurable": {"thread_id": thread_id},
        "run_name": f"plan_{mode}",
        "tags": ["tripmate", mode],
        "metadata": {"request_id": request_id, "thread_id": thread_id, "mode": mode},
    }
