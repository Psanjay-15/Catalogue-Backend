from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.models.template import Template
from app.db.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    collection_name = "templates"
    model = Template

    async def list_all(self, db: AsyncIOMotorDatabase) -> list[Template]:
        cursor = self.collection(db).find({}).sort("_id", 1)
        rows: list[Template] = []
        async for doc in cursor:
            template = Template.from_mongo(doc)
            if template is not None:
                rows.append(template)
        return rows


template_repo = TemplateRepository()
