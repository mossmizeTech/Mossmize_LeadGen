"""
MongoDB connection management using Motor (async driver).
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    """Establish MongoDB connection and create indexes."""
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongo_uri)
    _db = _client[settings.mongo_db_name]

    # Ensure indexes
    await _db.businesses.create_index("place_id", unique=True)
    await _db.businesses.create_index("website")
    await _db.businesses.create_index("city")
    await _db.emails.create_index("email")
    await _db.emails.create_index("business_id")
    await _db.emails.create_index([("email", 1), ("business_id", 1)], unique=True)


async def close_db() -> None:
    """Close MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
    _client = None
    _db = None


def get_db() -> AsyncIOMotorDatabase:
    """Return the active database handle."""
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _db
