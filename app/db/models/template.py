from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.db.models.catalog import utcnow


@dataclass(slots=True)
class Template:
    id: str
    name: str
    description: str
    kind: str
    sample_html: str
    created_at: datetime = field(default_factory=utcnow)

    @classmethod
    def from_mongo(cls, doc: dict[str, Any] | None) -> "Template | None":
        if doc is None:
            return None
        return cls(
            id=doc["_id"],
            name=doc["name"],
            description=doc["description"],
            kind=doc["kind"],
            sample_html=doc["sample_html"],
            created_at=doc["created_at"],
        )

    def to_mongo(self) -> dict[str, Any]:
        return {
            "_id": self.id,
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "sample_html": self.sample_html,
            "created_at": self.created_at,
        }
