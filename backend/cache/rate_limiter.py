import time

import redis

from backend import config
from backend.cache.redis_client import get_redis


def is_allowed(user_key: str) -> bool:
    """Fixed window: max N requests per user per minute."""
    client = get_redis()
    if client is None:
        return True

    window = int(time.time() // 60)
    key = f"rate:{user_key}:{window}"
    try:
        count = client.incr(key)
        if count == 1:
            client.expire(key, 60)
        return count <= config.RATE_LIMIT_PER_MINUTE
    except redis.RedisError:
        return True
