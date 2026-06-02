"""Catalog ORM model — one row per generation job."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, ForeignKey, LargeBinary, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


STATUS_QUEUED     = "queued"
STATUS_EXTRACTING = "extracting"
STATUS_REFINING   = "refining"
STATUS_RENDERING  = "rendering"
STATUS_EXPORTING  = "exporting"
STATUS_DONE       = "done"
STATUS_FAILED     = "failed"


class Catalog(Base):
    __tablename__ = "catalogs"

    id:            Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status:        Mapped[str] = mapped_column(String(32), nullable=False, index=True, default=STATUS_QUEUED)
    template_id:   Mapped[str] = mapped_column(String(64), ForeignKey("templates.id"), nullable=False)
    llm_provider:  Mapped[str] = mapped_column(String(32), nullable=False)
    style:         Mapped[str] = mapped_column(String(32), nullable=False, default="modern")
    theme:         Mapped[str] = mapped_column(String(16), nullable=False)
    page_size:     Mapped[str] = mapped_column(String(16), nullable=False)
    source_text:   Mapped[str] = mapped_column(Text, nullable=False)
    refined_json:  Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    html:          Mapped[str | None] = mapped_column(Text, nullable=True)
    # The exported PDF is stored in the database (as raw bytes), not on local
    # disk — generated on demand and cached here so downloads are instant.
    pdf_bytes:     Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    error:         Mapped[str | None] = mapped_column(Text, nullable=True)
    # "Saved Catalogs" library: a generation becomes a kept catalog when the
    # user explicitly saves it (and gives it a name). Per-user scoping is
    # intentionally deferred until auth lands — for now the library is shared.
    saved:         Mapped[bool] = mapped_column(Boolean, nullable=False, index=True, server_default="false", default=False)
    title:         Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at:    Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at:    Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
