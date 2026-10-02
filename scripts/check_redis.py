import asyncio

from backend.cache.redis_client import get_redis
from backend.graph.builder import close_graph, get_graph


async def main():
    client = get_redis()
    if client is None:
        print("Redis: NOT connected. Caching and rate limiting are off.")
    else:
        client.set("hello", "world", ex=10)
        print("Redis: connected, test value =", client.get("hello"))

    graph = await get_graph()
    print("Checkpointer type:", type(graph.checkpointer).__name__)
    await close_graph()


asyncio.run(main())
