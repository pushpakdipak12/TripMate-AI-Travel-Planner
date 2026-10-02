import functools
import json
import sys

import redis

from mcp_servers.settings import REDIS_URL

ONE_HOUR = 3600
ONE_DAY = 24 * ONE_HOUR

_client = None
_checked = False


def get_redis():
    """Connects once. Returns None if Redis is not running (app still works, just slower)."""
    global _client, _checked
    if not _checked:
        _checked = True
        try:
            client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            client.ping()
            _client = client
        except (redis.RedisError, ValueError):
            print("Redis not available: caching is off", file=sys.stderr)
    return _client


def cached(prefix: str, ttl_seconds: int, should_cache=bool, empty_ttl_seconds: int = 0):
    """
    Decorator: saves a function's result in Redis for ttl_seconds.
    empty_ttl_seconds: also remember empty results for a short time, so a slow
    or broken server is not called again on every request.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client = get_redis()
            key = f"cache:{prefix}:" + json.dumps([args, kwargs], sort_keys=True, default=str).lower()

            if client:
                try:
                    hit = client.get(key)
                    client.incr("stats:cache:hit" if hit is not None else "stats:cache:miss")
                    if hit is not None:
                        return json.loads(hit)
                except redis.RedisError:
                    pass

            result = func(*args, **kwargs)

            if client:
                ttl = ttl_seconds if should_cache(result) else empty_ttl_seconds
                if ttl:
                    try:
                        client.set(key, json.dumps(result), ex=ttl)
                    except redis.RedisError:
                        pass
            return result
        return wrapper
    return decorator
