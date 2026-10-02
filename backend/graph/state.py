import operator
from typing import Annotated, Optional, TypedDict


class TripState(TypedDict, total=False):
    # Input
    mode: str
    query: str
    selected_transport: Optional[str]   # set when the user picks an option

    # From the query parser
    trip: dict
    needs_clarification: bool
    question: Optional[str]

    # From the agents
    transport: dict
    recommended_transport: dict         # {"option_name": ..., "reason": ...}
    hotels: dict
    chosen_hotel: dict
    weather: dict
    activities: dict
    budget: dict
    itinerary: list

    # Control
    retries: int
    errors: Annotated[list, operator.add]   # parallel agents can all add errors
