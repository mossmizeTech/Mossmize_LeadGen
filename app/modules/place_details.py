"""
Business Details Fetcher
Uses Place Details API to get website, phone, opening hours for each business.
"""

import logging

import httpx

from app.config import settings
from app.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

_google_limiter = RateLimiter(max_per_second=settings.google_api_rps)

PLACE_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

# Only request the fields we need to minimize API costs
DETAIL_FIELDS = "name,website,formatted_phone_number,url,opening_hours,formatted_address"


async def fetch_details(place_id: str) -> dict:
    """
    Fetch detailed information for a business using Place Details API.

    Args:
        place_id: Google Place ID

    Returns:
        Dict with keys: website, phone_number, google_maps_url,
        opening_hours, formatted_address
    """
    await _google_limiter.acquire()

    params = {
        "place_id": place_id,
        "fields": DETAIL_FIELDS,
        "key": settings.google_maps_api_key,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.get(PLACE_DETAILS_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPError as e:
            logger.error("Place Details API failed for %s: %s", place_id, e)
            return {}

    status = data.get("status", "UNKNOWN")
    if status != "OK":
        logger.warning("Place Details status: %s for place_id=%s", status, place_id)
        return {}

    result = data.get("result", {})
    hours = result.get("opening_hours", {})

    return {
        "website": result.get("website"),
        "phone_number": result.get("formatted_phone_number"),
        "google_maps_url": result.get("url"),
        "opening_hours": hours.get("weekday_text", []),
        "formatted_address": result.get("formatted_address", ""),
    }
