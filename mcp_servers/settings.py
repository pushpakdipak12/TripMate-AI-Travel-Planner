import os

from dotenv import load_dotenv

load_dotenv()

USER_AGENT = os.getenv("USER_AGENT", "india-travel-planner/1.0 (your-email@example.com)")
IGNAV_API_KEY = os.getenv("IGNAV_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
HTTP_TIMEOUT = 30
