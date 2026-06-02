from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.catalog import Catalog
from app.db.repositories.base import BaseRepository


class CatalogRepository(BaseRepository[Catalog]):
    model = Catalog

    async def list_saved(
        self, db: AsyncSession, *, limit: int = 200, offset: int = 0
    ) -> list[Catalog]:
        """Catalogs the user explicitly saved, newest-touched first."""
        stmt = (
            select(Catalog)
            .where(Catalog.saved.is_(True))
            .order_by(Catalog.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(stmt)
        return list(result.scalars())


catalog_repo = CatalogRepository()
