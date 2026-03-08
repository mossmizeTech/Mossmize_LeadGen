"""
Website Discovery Fallback
Finds a business website when Google Maps doesn't provide one.
"""

import logging
import re
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

# Domains to exclude from search results
EXCLUDED_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com",
    "linkedin.com", "youtube.com", "tiktok.com", "pinterest.com",
    "yelp.com", "tripadvisor.com", "justdial.com", "indiamart.com",
    "google.com", "wikipedia.org", "maps.google.com",
}


async def discover_website(business_name: str, city: str) -> str | None:
    """
    Attempt to discover a business website by searching the web.

    Uses a simple Google search scrape as fallback.

    Args:
        business_name: name of the business
        city: city where the business is located

    Returns:
        Website URL or None if not found
    """
    query = f'"{business_name}" {city} official website'
    search_url = "https://www.google.com/search"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(search_url, params={"q": query}, headers=headers)
            resp.raise_for_status()
            html = resp.text
    except httpx.HTTPError as e:
        logger.warning("Website discovery search failed for '%s': %s", business_name, e)
        return None

    # Extract URLs from search results
    url_pattern = re.compile(r'href="(https?://[^"]+)"')
    matches = url_pattern.findall(html)

    for url in matches:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")

        # Skip excluded domains
        if any(excl in domain for excl in EXCLUDED_DOMAINS):
            continue

        # Skip Google-internal URLs
        if "google." in domain:
            continue

        # Return the first plausible business website
        return url

    logger.info("No website found for business '%s' in '%s'", business_name, city)
    return None
