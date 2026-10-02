# All prices are rough Indian estimates in rupees. Tune them anytime.

# Per person per km (low, high)
TRAIN_SLEEPER = (0.5, 0.8)
TRAIN_3AC = (1.2, 1.6)
GOVT_BUS = (1.0, 1.5)
PRIVATE_AC_BUS = (1.5, 2.5)

# Per vehicle per km (low, high)
CAB = (12, 18)              # up to 4 people per cab
SELF_DRIVE = (8, 11)        # fuel + tolls, up to 4 people per car

# Flights: per person = base + per_km * distance, high = low x multiplier
FLIGHT_BASE = 2000
FLIGHT_PER_KM = 2.5
FLIGHT_HIGH_MULTIPLIER = 1.8
AIRPORT_TIME_HOURS = 2.5

# Average speeds in km per hour
TRAIN_SPEED_SHORT = 45       # trips under 800 km
TRAIN_SPEED_LONG = 65        # long trips have faster express trains
LONG_TRAIN_KM = 800
BUS_SPEED = 45
ROAD_SPEED = 60

# Hotels: per room per night (low, high)
HOTEL_PER_NIGHT = {
    "budget": (1200, 2500),
    "mid": (3000, 6000),
    "luxury": (8000, 18000),
}
PREMIUM_CITIES = {"goa", "mumbai", "udaipur", "manali", "shimla", "delhi", "bangalore", "bengaluru"}
PREMIUM_MULTIPLIER = 1.2
