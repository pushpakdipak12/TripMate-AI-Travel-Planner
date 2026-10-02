import redis

from backend import config

_client = None
_checked = False


def get_redis():
    """Connects once. Returns None if Redis is not running."""
    global _client, _checked
    if not _checked:
        _checked = True
        try:
            client = redis.Redis.from_url(config.REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            client.ping()
            _client = client
        except (redis.RedisError, ValueError):
            print("Redis not available: rate limiting is off")
    return _client
