import json
import math
from pathlib import Path

from mcp_servers.geo import road_distance_km
from mcp_servers.pricing import rates

AIRPORTS_FILE = Path(__file__).resolve().parents[2] / "data" / "indian_airports.json"
AIRPORTS = json.loads(AIRPORTS_FILE.read_text(encoding="utf-8"))


def round_50(value: float) -> int:
    return int(round(value / 50) * 50)


def make_option(mode, name, hours, low, high, note):
    return {
        "mode": mode,
        "name": name,
        "duration_hours": round(hours, 1),
        "price_min": round_50(low),
        "price_max": round_50(high),
        "note": note,
    }


def compare_transport(origin: str, destination: str, travelers: int = 1) -> dict:
    km = road_distance_km(origin, destination)
    if km is None:
        return {"error": f"Could not find distance between {origin} and {destination}"}

    vehicles = math.ceil(travelers / 4)
    options = []

    if 50 <= km <= 2500:
        speed = rates.TRAIN_SPEED_LONG if km > rates.LONG_TRAIN_KM else rates.TRAIN_SPEED_SHORT
        hours = km / speed
        low, high = rates.TRAIN_SLEEPER
        options.append(make_option("train", "Train (Sleeper)", hours, low * km * travelers, high * km * travelers, "Cheapest, less comfortable"))
        low, high = rates.TRAIN_3AC
        options.append(make_option("train", "Train (3AC)", hours, low * km * travelers, high * km * travelers, "Comfortable, good value"))

    if km <= 1200:
        hours = km / rates.BUS_SPEED
        low, high = rates.GOVT_BUS
        options.append(make_option("bus", "Government bus", hours, low * km * travelers, high * km * travelers, "Budget friendly"))
        low, high = rates.PRIVATE_AC_BUS
        options.append(make_option("bus", "Private AC sleeper bus", hours, low * km * travelers, high * km * travelers, "Many departures, overnight option"))

    if km <= 800:
        low, high = rates.CAB
        options.append(make_option("cab", "Cab", km / rates.ROAD_SPEED, low * km * vehicles, high * km * vehicles, f"{vehicles} cab(s), door to door"))

    if km <= 1000:
        low, high = rates.SELF_DRIVE
        options.append(make_option("self_drive", "Self-drive", km / rates.ROAD_SPEED, low * km * vehicles, high * km * vehicles, "Fuel and tolls, flexible"))

    if km > 400:
        per_person = rates.FLIGHT_BASE + rates.FLIGHT_PER_KM * km
        hours = 0.75 + km / 1000 + rates.AIRPORT_TIME_HOURS
        has_airports = origin.strip().lower() in AIRPORTS and destination.strip().lower() in AIRPORTS
        if has_airports:
            note = "Fastest, includes airport time"
        else:
            hours += 1.5
            note = "Via nearest airport, may need extra local travel"
        options.append(make_option("flight", "Flight", hours, per_person * travelers, per_person * travelers * rates.FLIGHT_HIGH_MULTIPLIER, note))

    return {
        "origin": origin,
        "destination": destination,
        "distance_km": round(km),
        "travelers": travelers,
        "price_basis": "One way, total for all travelers, estimated",
        "options": options,
    }
