"""
Website Crawler
Crawls business websites to extract page content for email extraction.
Uses httpx + BeautifulSoup for static pages, with Playwright fallback for JS-heavy sites.
"""

import asyncio
import logging
import random
import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)

# Priority pages to crawl on each website
PRIORITY_PATHS = [
    "/",
    "/contact",
    "/contact-us",
    "/about",
    "/about-us",
    "/team",
    "/support",
    "/careers",
]

# Default headers for crawler
CRAWLER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _is_internal_link(url: str, base_domain: str) -> bool:
    """Check if a URL belongs to the same domain."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return domain == base_domain or domain == ""
    except Exception:
        return False


def _extract_links(html: str, base_url: str, base_domain: str) -> list[str]:
    """Extract internal links from HTML content."""
    soup = BeautifulSoup(html, "lxml")
    links: set[str] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
            continue
        full_url = urljoin(base_url, href)
        if _is_internal_link(full_url, base_domain):
            # Normalize: remove fragment, keep path
            parsed = urlparse(full_url)
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            links.add(clean_url.rstrip("/"))

    return list(links)


async def _fetch_page(client: httpx.AsyncClient, url: str) -> str | None:
    """Fetch a single page, return HTML or None on failure."""
    try:
        resp = await client.get(url, headers=CRAWLER_HEADERS, follow_redirects=True, timeout=15)
        content_type = resp.headers.get("content-type", "")
        if "text/html" not in content_type:
            return None
        resp.raise_for_status()
        return resp.text
    except (httpx.HTTPError, Exception) as e:
        logger.debug("Failed to fetch %s: %s", url, e)
        return None


async def _fetch_page_playwright(url: str) -> str | None:
    """Fetch a page using Playwright for JS-rendered content."""
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("Playwright not installed, skipping JS rendering for %s", url)
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=20000)
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        logger.warning("Playwright failed for %s: %s", url, e)
        return None


async def crawl_website(website_url: str) -> list[dict]:
    """
    Crawl a business website and return page contents.

    Crawls priority pages first, then discovered internal links
    up to max_crawl_depth and max_pages_per_site.

    Args:
        website_url: root URL of the website

    Returns:
        List of {"url": str, "html": str} for each crawled page
    """
    parsed = urlparse(website_url)
    base_domain = parsed.netloc.lower().replace("www.", "")
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    visited: set[str] = set()
    pages: list[dict] = []
    max_pages = settings.max_pages_per_site
    max_depth = settings.max_crawl_depth

    # Build initial URL queue: priority paths
    queue: list[tuple[str, int]] = []  # (url, depth)
    for path in PRIORITY_PATHS:
        full_url = urljoin(base_url, path).rstrip("/")
        if full_url not in visited:
            queue.append((full_url, 0))

    async with httpx.AsyncClient() as client:
        while queue and len(pages) < max_pages:
            url, depth = queue.pop(0)
            normalized = url.rstrip("/")

            if normalized in visited:
                continue
            visited.add(normalized)

            # Rate limiting: random delay between crawl requests
            delay = random.uniform(settings.crawl_delay_min, settings.crawl_delay_max)
            await asyncio.sleep(delay)

            # Try static fetch first
            html = await _fetch_page(client, url)

            # If static fetch returned very little content, try Playwright
            if html and len(html) < 500:
                pw_html = await _fetch_page_playwright(url)
                if pw_html and len(pw_html) > len(html):
                    html = pw_html
            elif html is None:
                html = await _fetch_page_playwright(url)

            if not html:
                continue

            pages.append({"url": url, "html": html})

            # Discover more internal links if within depth limit
            if depth < max_depth:
                new_links = _extract_links(html, url, base_domain)
                for link in new_links:
                    if link.rstrip("/") not in visited:
                        queue.append((link, depth + 1))

    logger.info("Crawled %d pages from %s", len(pages), website_url)
    return pages
