"""
Google Maps Search Module
Uses Places Nearby Search API to find businesses by keyword + location.
"""

import asyncio
import logging

import httpx

from app.config import settings
from app.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

_google_limiter = RateLimiter(max_per_second=settings.google_api_rps)

NEARBY_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


async def search_nearby(
    keyword: str,
    lat: float,
    lng: float,
    radius: int = 5000,
) -> list[dict]:
    """
    Search for businesses near a coordinate using Places Nearby Search API.
    Handles pagination via next_page_token.

    Args:
        keyword: search term (e.g. "dentist")
        lat: latitude of grid center
        lng: longitude of grid center
        radius: search radius in meters (default 5000 = 5 km)

    Returns:
        List of business dicts with keys:
            business_name, place_id, address, rating,
            user_ratings_total, latitude, longitude
    """
    businesses: list[dict] = []
    next_page_token: str | None = None

    async with httpx.AsyncClient(timeout=30) as client:
        while True:
            await _google_limiter.acquire()

            params: dict = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "keyword": keyword,
                "key": settings.google_maps_api_key,
            }
            if next_page_token:
                params["pagetoken"] = next_page_token

            try:
                resp = await client.get(NEARBY_SEARCH_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
            except httpx.HTTPError as e:
                logger.error("Places Nearby Search failed: %s", e)
                break

            status = data.get("status", "UNKNOWN")
            if status not in ("OK", "ZERO_RESULTS"):
                logger.warning("Nearby Search status: %s (keyword=%s, loc=%s,%s)", status, keyword, lat, lng)
                break

            for place in data.get("results", []):
                loc = place.get("geometry", {}).get("location", {})
                businesses.append({
                    "business_name": place.get("name", ""),
                    "place_id": place.get("place_id", ""),
                    "address": place.get("vicinity", ""),
                    "rating": place.get("rating"),
                    "user_ratings_total": place.get("user_ratings_total"),
                    "latitude": loc.get("lat", 0.0),
                    "longitude": loc.get("lng", 0.0),
                    "types": place.get("types", []),
                })

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

            # Google requires a short delay before using next_page_token
            await asyncio.sleep(2)

    logger.info(
        "Found %d businesses for keyword='%s' at (%s, %s)",
        len(businesses), keyword, lat, lng,
    )
    return businesses
