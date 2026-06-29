from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.db.models.catalog import Catalog
from app.db.repositories.base import BaseRepository


class CatalogRepository(BaseRepository[Catalog]):
    collection_name = "catalogs"
    model = Catalog

    async def list_saved(
        self,
        db: AsyncIOMotorDatabase,
        *,
        limit: int = 200,
        offset: int = 0,
    ) -> list[Catalog]:
        cursor = (
            self.collection(db)
            .find({"saved": True})
            .sort("updated_at", DESCENDING)
            .skip(offset)
            .limit(limit)
        )
        rows: list[Catalog] = []
        async for doc in cursor:
            catalog = Catalog.from_mongo(doc)
            if catalog is not None:
                rows.append(catalog)
        return rows


catalog_repo = CatalogRepository()
