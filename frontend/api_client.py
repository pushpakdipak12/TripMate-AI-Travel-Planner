import os

import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")


class ApiError(Exception):
    pass


def _post(path: str, payload: dict) -> dict:
    try:
        response = requests.post(f"{API_URL}{path}", json=payload, timeout=300)
    except requests.RequestException:
        raise ApiError("The planner is offline. Start the backend with: uvicorn backend.main:app")
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise ApiError(str(detail))
    return response.json()


def plan(mode: str, query: str) -> dict:
    return _post("/plan", {"mode": mode, "query": query})


def replan(thread_id: str, option_name: str) -> dict:
    return _post("/replan", {"thread_id": thread_id, "selected_transport": option_name})


def health() -> dict | None:
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.json() if response.ok else None
    except requests.RequestException:
        return None


def stats() -> dict | None:
    try:
        response = requests.get(f"{API_URL}/stats", timeout=5)
        return response.json() if response.ok else None
    except requests.RequestException:
        return None
