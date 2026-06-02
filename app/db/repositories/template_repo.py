from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.template import Template
from app.db.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    model = Template

    async def list_all(self, db: AsyncSession) -> list[Template]:
        """Return all templates sorted by id — used by GET /templates."""
        stmt = select(Template).order_by(Template.id)
        result = await db.execute(stmt)
        return list(result.scalars())


template_repo = TemplateRepository()
