from pathlib import Path

import aiosqlite
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from backend import config

PLAN_TTL_MINUTES = 24 * 60     # saved plans in Redis expire after 1 day
SQLITE_FILE = Path(__file__).resolve().parents[2] / "data" / "checkpoints.db"


async def create_checkpointer():
    """
    1. Redis (best): fast and shared, needs Redis with the search module.
    2. SQLite (fallback): a local file, so plans still survive a restart.
    """
    try:
        saver = AsyncRedisSaver(
            redis_url=config.REDIS_URL,
            ttl={"default_ttl": PLAN_TTL_MINUTES, "refresh_on_read": True},
        )
        await saver.asetup()
        print("Checkpointer: Redis")
        return saver
    except Exception as e:
        print(f"Checkpointer: SQLite file (Redis not usable: {str(e)[:80]})")

    connection = await aiosqlite.connect(SQLITE_FILE)
    saver = AsyncSqliteSaver(connection)
    await saver.setup()
    return saver
