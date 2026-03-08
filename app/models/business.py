"""
Pydantic model for the businesses collection.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class BusinessDoc(BaseModel):
    """Schema for a business document in MongoDB."""

    business_name: str
    place_id: str
    address: str = ""
    website: Optional[str] = None
    phone: Optional[str] = None
    city: str = ""
    category: Optional[str] = None
    latitude: float = 0.0
    longitude: float = 0.0
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    google_maps_url: Optional[str] = None
    opening_hours: Optional[list[str]] = None
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        """Convert to MongoDB-compatible dict."""
        data = self.model_dump()
        data["scraped_at"] = self.scraped_at
        return data
