from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base


class Template(Base):
    __tablename__ = "templates"

    id:           Mapped[str] = mapped_column(String(64), primary_key=True)
    name:         Mapped[str] = mapped_column(String(120), nullable=False)
    description:  Mapped[str] = mapped_column(Text, nullable=False)
    kind:         Mapped[str] = mapped_column(String(32), nullable=False)
    sample_html:  Mapped[str] = mapped_column(Text, nullable=False)
    created_at:   Mapped[datetime] = mapped_column(server_default=func.now())
