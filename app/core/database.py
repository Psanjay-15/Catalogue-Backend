from __future__ import annotations
from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.config import settings


class Base(DeclarativeBase):
    """Declarative base — all ORM models inherit from this."""
    pass


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a session, ensures it's closed on exit."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


_ADDITIVE_MIGRATIONS: tuple[str, ...] = (
    "ALTER TABLE catalogs ADD COLUMN IF NOT EXISTS saved boolean NOT NULL DEFAULT false",
    "ALTER TABLE catalogs ADD COLUMN IF NOT EXISTS title varchar(200)",
    "CREATE INDEX IF NOT EXISTS ix_catalogs_saved ON catalogs (saved)",
    "ALTER TABLE catalogs ADD COLUMN IF NOT EXISTS pdf_bytes bytea",
    "ALTER TABLE catalogs DROP COLUMN IF EXISTS pdf_path",
)


async def create_all() -> None:

    from app.db.models import catalog, template 

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        for stmt in _ADDITIVE_MIGRATIONS:
            await conn.execute(text(stmt))
