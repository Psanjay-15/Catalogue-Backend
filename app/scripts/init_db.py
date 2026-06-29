"""Create MongoDB collections, validators, and indexes.

Idempotent.

Run with:
    python -m app.scripts.init_db
"""

from __future__ import annotations

import asyncio

from app.core.database import close_database, init_database
from app.core.logging import configure_logging, get_logger


async def main() -> None:
    configure_logging()
    log = get_logger("init_db")
    log.info("initializing MongoDB collections...")
    await init_database()
    await close_database()
    log.info("done")


if __name__ == "__main__":
    asyncio.run(main())
