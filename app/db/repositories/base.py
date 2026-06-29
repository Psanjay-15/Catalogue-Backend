from __future__ import annotations

from typing import Any, Generic, Protocol, TypeVar

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.catalog import utcnow


class MongoModel(Protocol):
    def to_mongo(self) -> dict[str, Any]: ...


ModelT = TypeVar("ModelT", bound=MongoModel)


class BaseRepository(Generic[ModelT]):
    collection_name: str
    model: type[ModelT]

    def collection(self, db: AsyncIOMotorDatabase):
        return db[self.collection_name]

    async def get(self, db: AsyncIOMotorDatabase, id_: Any) -> ModelT | None:
        doc = await self.collection(db).find_one({"_id": str(id_)})
        return self.model.from_mongo(doc)  # type: ignore[attr-defined]

    async def create(self, db: AsyncIOMotorDatabase, obj: ModelT) -> ModelT:
        await self.collection(db).insert_one(obj.to_mongo())
        return obj

    async def update(self, db: AsyncIOMotorDatabase, id_: Any, **fields: Any) -> ModelT | None:
        fields["updated_at"] = utcnow()
        await self.collection(db).update_one({"_id": str(id_)}, {"$set": fields})
        return await self.get(db, id_)

    async def upsert_by_id(
        self,
        db: AsyncIOMotorDatabase,
        id_: Any,
        defaults: dict[str, Any],
    ) -> ModelT:
        now = utcnow()
        doc = {
            **defaults,
            "created_at": defaults.get("created_at", now),
        }
        await self.collection(db).update_one(
            {"_id": str(id_)},
            {
                "$set": {k: v for k, v in doc.items() if k != "created_at"},
                "$setOnInsert": {"created_at": doc["created_at"]},
            },
            upsert=True,
        )
        obj = await self.get(db, id_)
        if obj is None:
            raise RuntimeError(f"Failed to upsert {self.collection_name}.{id_}")
        return obj
