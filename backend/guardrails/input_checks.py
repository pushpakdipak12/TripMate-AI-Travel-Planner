import re

MAX_QUERY_LENGTH = 300

# Common prompt-injection phrases. Travel queries never need these.
INJECTION_PATTERNS = [
    r"ignore (all |the |your )?(previous|above|earlier) (instructions|rules|prompts?)",
    r"forget (all |your )?(instructions|rules)",
    r"system prompt",
    r"reveal .*(prompt|instructions)",
    r"you are now",
    r"jailbreak",
    r"developer mode",
]

PHONE = re.compile(r"(\+91[\-\s]?)?\b[6-9]\d{9}\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")


class InputRejected(Exception):
    pass


def mask_pii(text: str) -> str:
    """Hide phone numbers and emails before the text reaches the LLM."""
    return EMAIL.sub("[EMAIL]", PHONE.sub("[PHONE]", text))


def check_input(query: str) -> str:
    """Returns a safe, masked query or raises InputRejected."""
    query = query.strip()
    if not query:
        raise InputRejected("Please enter a query.")
    if len(query) > MAX_QUERY_LENGTH:
        raise InputRejected(f"Query is too long. Please keep it under {MAX_QUERY_LENGTH} characters.")
    lowered = query.lower()
    if any(re.search(pattern, lowered) for pattern in INJECTION_PATTERNS):
        raise InputRejected("Sorry, I can only help with travel planning.")
    return mask_pii(query)


def check_trip_limits(trip) -> str | None:
    """Sanity limits after parsing. Returns a question for the user, or None."""
    if trip.days is not None and not 1 <= trip.days <= 30:
        return "Please choose a trip between 1 and 30 days."
    if not 1 <= trip.travelers <= 20:
        return "We can plan for 1 to 20 travellers."
    if trip.budget_inr is not None and trip.budget_inr < 1000:
        return "The budget looks too small. Please enter your total budget in rupees."
    return None
