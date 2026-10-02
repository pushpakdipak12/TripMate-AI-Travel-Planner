from pydantic import BaseModel, Field


class TransportChoice(BaseModel):
    option_name: str = Field(description="Exact name of the chosen option")
    reason: str = Field(description="1-2 simple sentences explaining why")


class DayPlan(BaseModel):
    day: int
    title: str = Field(description="Short title, e.g. Beaches of North Goa")
    plan: str = Field(description="2-3 sentences: morning, afternoon, evening")


class Itinerary(BaseModel):
    days: list[DayPlan]


class PlaceList(BaseModel):
    places: list[str] = Field(description="Names of real tourist places")
