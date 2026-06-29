from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pymongo.errors import CollectionInvalid, OperationFailure

from app.config import settings
from app.core.logging import get_logger


log = get_logger(__name__)

_client: AsyncIOMotorClient | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.mongodb_uri,
            uuidRepresentation="standard",
            serverSelectionTimeoutMS=10_000,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_mongo_client()[settings.mongodb_database]


async def get_session() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
   
    yield get_database()


async def close_database() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


_CATALOG_VALIDATOR: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "_id",
            "status",
            "template_id",
            "llm_provider",
            "style",
            "theme",
            "page_size",
            "source_text",
            "saved",
            "created_at",
            "updated_at",
        ],
        "properties": {
            "_id": {"bsonType": "string"},
            "status": {"bsonType": "string"},
            "template_id": {"bsonType": "string"},
            "llm_provider": {"bsonType": "string"},
            "style": {"bsonType": "string"},
            "theme": {"bsonType": "string"},
            "page_size": {"bsonType": "string"},
            "source_text": {"bsonType": "string"},
            "refined_json": {"bsonType": ["object", "null"]},
            "html": {"bsonType": ["string", "null"]},
            "pdf_bytes": {"bsonType": ["binData", "null"]},
            "error": {"bsonType": ["string", "null"]},
            "saved": {"bsonType": "bool"},
            "title": {"bsonType": ["string", "null"]},
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}

_TEMPLATE_VALIDATOR: dict[str, Any] = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["_id", "name", "description", "kind", "sample_html", "created_at"],
        "properties": {
            "_id": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "kind": {"bsonType": "string"},
            "sample_html": {"bsonType": "string"},
            "created_at": {"bsonType": "date"},
        },
    }
}


async def _ensure_collection(
    db: AsyncIOMotorDatabase,
    name: str,
    validator: dict[str, Any],
) -> None:
    try:
        await db.create_collection(name, validator=validator)
    except CollectionInvalid:
        try:
            await db.command("collMod", name, validator=validator)
        except OperationFailure as exc:
            log.warning("could not update Mongo validator for %s: %s", name, exc)


async def init_database() -> None:
    """Create Mongo collections, validators, and indexes if they do not exist."""
    db = get_database()
    await get_mongo_client().admin.command("ping")

    await _ensure_collection(db, "catalogs", _CATALOG_VALIDATOR)
    await _ensure_collection(db, "templates", _TEMPLATE_VALIDATOR)

    await db.catalogs.create_index([("status", ASCENDING)])
    await db.catalogs.create_index([("saved", ASCENDING), ("updated_at", DESCENDING)])
    await db.catalogs.create_index([("template_id", ASCENDING)])
    await db.templates.create_index([("kind", ASCENDING)])


# Backward-compatible alias for old scripts/imports.
create_all = init_database
