"""Catalog document model — one MongoDB document per generation job."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


STATUS_QUEUED = "queued"
STATUS_EXTRACTING = "extracting"
STATUS_REFINING = "refining"
STATUS_RENDERING = "rendering"
STATUS_EXPORTING = "exporting"
STATUS_DONE = "done"
STATUS_FAILED = "failed"


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Catalog:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    status: str = STATUS_QUEUED
    template_id: str = "ai"
    llm_provider: str = "gemini"
    style: str = "modern"
    theme: str = "light"
    page_size: str = "A4"
    source_text: str = ""
    refined_json: dict[str, Any] | None = None
    html: str | None = None
    pdf_bytes: bytes | None = None
    error: str | None = None
    saved: bool = False
    title: str | None = None
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)

    @classmethod
    def from_mongo(cls, doc: dict[str, Any] | None) -> "Catalog | None":
        if doc is None:
            return None
        return cls(
            id=uuid.UUID(str(doc["_id"])),
            status=doc["status"],
            template_id=doc["template_id"],
            llm_provider=doc["llm_provider"],
            style=doc.get("style", "modern"),
            theme=doc["theme"],
            page_size=doc["page_size"],
            source_text=doc["source_text"],
            refined_json=doc.get("refined_json"),
            html=doc.get("html"),
            pdf_bytes=bytes(doc["pdf_bytes"]) if doc.get("pdf_bytes") is not None else None,
            error=doc.get("error"),
            saved=bool(doc.get("saved", False)),
            title=doc.get("title"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
        )

    def to_mongo(self) -> dict[str, Any]:
        return {
            "_id": str(self.id),
            "status": self.status,
            "template_id": self.template_id,
            "llm_provider": self.llm_provider,
            "style": self.style,
            "theme": self.theme,
            "page_size": self.page_size,
            "source_text": self.source_text,
            "refined_json": self.refined_json,
            "html": self.html,
            "pdf_bytes": self.pdf_bytes,
            "error": self.error,
            "saved": self.saved,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
