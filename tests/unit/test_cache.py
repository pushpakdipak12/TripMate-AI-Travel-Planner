import fakeredis
import pytest

import mcp_servers.cache as cache


@pytest.fixture
def fake_redis(monkeypatch):
    client = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(cache, "get_redis", lambda: client)
    return client


def test_second_call_comes_from_cache(fake_redis):
    calls = []

    @cache.cached("demo", 60)
    def lookup(city):
        calls.append(city)
        return {"city": city}

    assert lookup("Goa") == lookup("goa") == {"city": "Goa"}
    assert calls == ["Goa"]
    assert fake_redis.get("stats:cache:hit") == "1"


def test_empty_results_use_short_ttl(fake_redis):
    @cache.cached("empty", 7 * cache.ONE_DAY, empty_ttl_seconds=cache.ONE_HOUR)
    def lookup(city):
        return []

    lookup("Nowhere")
    key = next(k for k in fake_redis.keys("cache:empty:*"))
    assert 0 < fake_redis.ttl(key) <= cache.ONE_HOUR
