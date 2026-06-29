"""FastAPI dependencies (dependency-injection helpers)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_session


SessionDep = Annotated[AsyncIOMotorDatabase, Depends(get_session)]
