"""
Email Pattern Generation
Generates common email patterns when no email is found on the website.
"""

from urllib.parse import urlparse


# Common email prefixes used by businesses
COMMON_PREFIXES = [
    "info",
    "contact",
    "sales",
    "hello",
    "admin",
    "support",
    "office",
    "enquiry",
    "mail",
    "general",
]


def extract_domain(website_url: str) -> str | None:
    """
    Extract the root domain from a website URL.

    Args:
        website_url: full URL (e.g. "https://www.company.com/about")

    Returns:
        Domain string (e.g. "company.com") or None
    """
    try:
        parsed = urlparse(website_url)
        domain = parsed.netloc.lower().replace("www.", "")
        if domain:
            return domain
    except Exception:
        pass
    return None


def generate_pattern_emails(website_url: str) -> list[str]:
    """
    Generate common email patterns from a website domain.

    Args:
        website_url: business website URL

    Returns:
        List of potential email addresses (e.g. ["info@company.com", ...])
    """
    domain = extract_domain(website_url)
    if not domain:
        return []

    return [f"{prefix}@{domain}" for prefix in COMMON_PREFIXES]
