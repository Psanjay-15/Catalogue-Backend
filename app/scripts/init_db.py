"""Create all database tables.

This is the Phase-2 replacement for `alembic upgrade head`. Idempotent.

Run with:
    python -m app.scripts.init_db
"""

from __future__ import annotations

import asyncio

from app.core.database import create_all
from app.core.logging import configure_logging, get_logger


async def main() -> None:
    configure_logging()
    log = get_logger("init_db")
    log.info("creating tables (if missing)...")
    await create_all()
    log.info("done")


if __name__ == "__main__":
    asyncio.run(main())
