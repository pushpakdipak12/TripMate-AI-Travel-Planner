from typing import Optional

from pydantic import BaseModel

from backend.models.trip_query import Mode


class ParseRequest(BaseModel):
    mode: Mode
    query: str


class PlanRequest(BaseModel):
    mode: Mode
    query: str


class ReplanRequest(BaseModel):
    thread_id: str
    selected_transport: str
