from typing import Literal, Optional

from pydantic import BaseModel, Field

Mode = Literal["full_trip", "transport", "hotels", "weather", "activities", "budget"]


# Strict JSON schema rule: every field must be present in the LLM's answer.
# Optional[...] means the LLM can send null when the user didn't mention it.
class TripQuery(BaseModel):
    origin: Optional[str] = Field(description="Starting city, e.g. Pune. null if not mentioned")
    destination: Optional[str] = Field(description="Destination city, e.g. Goa. null if not mentioned")
    start_date: Optional[str] = Field(description="Start date as YYYY-MM-DD. null if not mentioned")
    days: Optional[int] = Field(description="Number of days or nights. null if not mentioned")
    travelers: int = Field(description="Number of people. 1 if not mentioned")
    budget_inr: Optional[int] = Field(description="Total budget in rupees. null if not mentioned")
    travel_style: Literal["budget", "mid", "luxury"] = Field(description="mid if not mentioned")
    interests: list[str] = Field(description="e.g. beaches, food. Empty list if none")


class ParseResult(BaseModel):
    mode: Mode
    trip: TripQuery
    missing_fields: list[str] = []
    needs_clarification: bool = False
    question: Optional[str] = None
