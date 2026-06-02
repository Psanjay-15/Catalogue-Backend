from __future__ import annotations
from typing import Any, Generic, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import Base
ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]                      

    async def get(self, db: AsyncSession, id_: Any) -> ModelT | None:
        return await db.get(self.model, id_)

    async def create(self, db: AsyncSession, obj: ModelT) -> ModelT:
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, id_: Any, **fields: Any) -> ModelT | None:
        obj = await self.get(db, id_)
        if obj is None:
            return None
        for k, v in fields.items():
            setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    async def upsert_by_id(self, db: AsyncSession, id_: Any, defaults: dict[str, Any]) -> ModelT:
        """Insert-or-update by primary key. Used by `generate_previews.py` to seed templates."""
        obj = await self.get(db, id_)
        if obj is None:
            obj = self.model(id=id_, **defaults)
            db.add(obj)
        else:
            for k, v in defaults.items():
                setattr(obj, k, v)
        await db.commit()
        await db.refresh(obj)
        return obj
