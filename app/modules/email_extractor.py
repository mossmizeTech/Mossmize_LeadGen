"""
Email Extraction Module
Extracts email addresses from HTML content using regex, mailto links, and structured data.
"""

import re
import logging
from typing import Set

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Email regex pattern
EMAIL_PATTERN = re.compile(
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
    re.IGNORECASE,
)

# Prefixes of emails to keep (high-value business contacts)
VALUABLE_PREFIXES = {
    "info", "contact", "sales", "support", "admin", "hello",
    "enquiry", "enquiries", "office", "mail", "help",
    "marketing", "business", "general", "team", "hr",
}

# Prefixes/patterns to discard
IGNORE_PREFIXES = {
    "noreply", "no-reply", "no_reply", "donotreply",
    "example", "test", "demo", "sample", "user",
    "username", "email", "your", "name",
}

# Domains to ignore (not real business emails)
IGNORE_DOMAINS = {
    "example.com", "example.org", "test.com",
    "sentry.io", "wixpress.com", "googleapis.com",
    "w3.org", "schema.org", "facebook.com",
    "twitter.com", "instagram.com",
}


def _is_valid_email(email: str) -> bool:
    """Check if an email should be kept."""
    email_lower = email.lower()
    local_part = email_lower.split("@")[0]
    domain = email_lower.split("@")[1] if "@" in email_lower else ""

    # Ignore blacklisted prefixes
    for prefix in IGNORE_PREFIXES:
        if local_part == prefix or local_part.startswith(prefix + "@"):
            return False

    # Ignore blacklisted domains
    if domain in IGNORE_DOMAINS:
        return False

    # Ignore image file extensions sometimes caught by regex
    if domain.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
        return False

    return True


def extract_emails_from_html(html: str, source_url: str = "") -> list[dict]:
    """
    Extract emails from HTML content.

    Checks:
    - Raw regex matches in HTML text
    - mailto: links
    - Structured data (JSON-LD)

    Args:
        html: raw HTML string
        source_url: URL the HTML was fetched from

    Returns:
        List of {"email": str, "source_page": str}
    """
    found_emails: Set[str] = set()
    results: list[dict] = []

    soup = BeautifulSoup(html, "lxml")

    # 1. Extract from mailto links
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.lower().startswith("mailto:"):
            raw = href[7:].split("?")[0].strip()
            if EMAIL_PATTERN.match(raw):
                found_emails.add(raw.lower())

    # 2. Extract from page text (body)
    page_text = soup.get_text(separator=" ")
    for match in EMAIL_PATTERN.findall(page_text):
        found_emails.add(match.lower())

    # 3. Extract from raw HTML (catches emails in attributes, comments, etc.)
    for match in EMAIL_PATTERN.findall(html):
        found_emails.add(match.lower())

    # 4. Extract from structured data (JSON-LD)
    for script in soup.find_all("script", type="application/ld+json"):
        if script.string:
            for match in EMAIL_PATTERN.findall(script.string):
                found_emails.add(match.lower())

    # Filter and build results
    for email in found_emails:
        if _is_valid_email(email):
            results.append({
                "email": email,
                "source_page": source_url,
            })

    logger.debug("Extracted %d emails from %s", len(results), source_url)
    return results


def extract_emails_from_pages(pages: list[dict]) -> list[dict]:
    """
    Extract emails from multiple crawled pages.

    Args:
        pages: list of {"url": str, "html": str}

    Returns:
        Deduplicated list of {"email": str, "source_page": str}
    """
    all_emails: list[dict] = []
    seen: set[str] = set()

    for page in pages:
        page_emails = extract_emails_from_html(page["html"], page.get("url", ""))
        for entry in page_emails:
            if entry["email"] not in seen:
                seen.add(entry["email"])
                all_emails.append(entry)

    return all_emails
