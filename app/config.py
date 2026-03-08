"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central settings for the Lead Generation system."""

    # Google Maps API
    google_maps_api_key: str = Field(..., description="Google Maps Platform API key")

    # MongoDB
    mongo_uri: str = Field("mongodb://localhost:27017", description="MongoDB connection URI")
    mongo_db_name: str = Field("lead_generation", description="MongoDB database name")

    # Redis / Celery
    redis_url: str = Field("redis://localhost:6379/0", description="Redis connection URL")

    # Rate Limiting
    google_api_rps: int = Field(10, description="Google API requests per second")
    crawl_delay_min: float = Field(2.0, description="Minimum delay between crawl requests (seconds)")
    crawl_delay_max: float = Field(5.0, description="Maximum delay between crawl requests (seconds)")

    # Crawling
    max_crawl_depth: int = Field(2, description="Maximum crawl depth per site")
    max_pages_per_site: int = Field(10, description="Maximum pages to crawl per site")

    # Grid
    grid_size_km: float = Field(5.0, description="Grid tile size in km")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
