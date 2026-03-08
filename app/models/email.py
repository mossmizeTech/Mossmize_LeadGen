"""
Pydantic model for the emails collection.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class EmailDoc(BaseModel):
    """Schema for an email document in MongoDB."""

    business_id: str  # string representation of ObjectId
    email: str
    source_page: Optional[str] = None
    validated: bool = False
    validation_method: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_mongo(self) -> dict:
        """Convert to MongoDB-compatible dict."""
        data = self.model_dump()
        data["created_at"] = self.created_at
        return data
