from functools import lru_cache

from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from backend import config
from backend.observability.logging import log_event
from backend.observability.metrics import record_fallback


def get_groq():
    return ChatGroq(
        model=config.GROQ_MODEL,
        api_key=config.GROQ_API_KEY,
        temperature=0,
        timeout=30,
        max_retries=1,
    )


def get_ollama():
    return ChatOllama(
        model=config.OLLAMA_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=0,
    )


def _fallback_started(value):
    """Runs just before Ollama takes over, so we can see it in logs and metrics."""
    record_fallback()
    log_event("llm fallback used", model=config.OLLAMA_MODEL)
    return value


@lru_cache
def get_structured_llm(schema):
    """
    1. Groq with strict JSON schema: the model can only produce valid JSON
       that matches our Pydantic model (no tool calling, no broken JSON).
    2. Retry up to 3 times for network or server errors.
    3. If Groq still fails, Ollama answers instead (logged and counted).
    """
    groq = (
        get_groq()
        .with_structured_output(schema, method="json_schema", strict=True)
        .with_retry(stop_after_attempt=3)
    )
    ollama = RunnableLambda(_fallback_started) | get_ollama().with_structured_output(schema)
    return groq.with_fallbacks([ollama])
