"""
Email Validation Module
Validates emails through regex, MX record checks, deduplication, and optional SMTP verification.
"""

import re
import logging
import asyncio
from typing import Optional

import dns.resolver

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(
    r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
)


def validate_regex(email: str) -> bool:
    """Step 1: Basic regex validation."""
    return bool(EMAIL_REGEX.match(email))


async def check_mx_record(domain: str) -> bool:
    """
    Step 2: Check if the domain has valid MX records.
    Runs DNS lookup in a thread to avoid blocking the event loop.
    """
    def _lookup():
        try:
            records = dns.resolver.resolve(domain, "MX")
            return len(records) > 0
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
                dns.resolver.NoNameservers, dns.exception.Timeout):
            return False
        except Exception as e:
            logger.debug("MX lookup error for %s: %s", domain, e)
            return False

    return await asyncio.to_thread(_lookup)


async def smtp_verify(email: str) -> Optional[bool]:
    """
    Step 4 (optional): SMTP VRFY check.
    Returns True if verified, False if rejected, None if inconclusive.

    NOTE: Many mail servers block VRFY. This is best-effort.
    """
    import smtplib

    domain = email.split("@")[1]

    def _verify():
        try:
            records = dns.resolver.resolve(domain, "MX")
            mx_host = str(records[0].exchange).rstrip(".")
        except Exception:
            return None

        try:
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_host, 25)
            server.helo("leadgen.local")
            code, _ = server.verify(email)
            server.quit()
            if code == 250:
                return True
            elif code == 550:
                return False
            return None  # Inconclusive
        except Exception:
            return None

    return await asyncio.to_thread(_verify)


async def validate_email(email: str, do_smtp: bool = False) -> dict:
    """
    Full validation pipeline for a single email.

    Steps:
        1. Regex validation
        2. MX record check
        3. (Dedup handled externally)
        4. Optional SMTP verify

    Args:
        email: email address to validate
        do_smtp: whether to perform SMTP verification

    Returns:
        {
            "email": str,
            "valid": bool,
            "method": str,  # "regex" | "mx" | "smtp"
            "details": str
        }
    """
    email = email.strip().lower()

    # Step 1: Regex
    if not validate_regex(email):
        return {
            "email": email,
            "valid": False,
            "method": "regex",
            "details": "Failed regex validation",
        }

    # Step 2: MX record
    domain = email.split("@")[1]
    has_mx = await check_mx_record(domain)
    if not has_mx:
        return {
            "email": email,
            "valid": False,
            "method": "mx",
            "details": f"No MX records for domain {domain}",
        }

    # Step 4: Optional SMTP
    if do_smtp:
        smtp_result = await smtp_verify(email)
        if smtp_result is False:
            return {
                "email": email,
                "valid": False,
                "method": "smtp",
                "details": "SMTP verification rejected",
            }
        method = "smtp" if smtp_result is True else "mx"
    else:
        method = "mx"

    return {
        "email": email,
        "valid": True,
        "method": method,
        "details": "Passed all validation checks",
    }


async def validate_emails(emails: list[str], do_smtp: bool = False) -> list[dict]:
    """
    Validate a batch of emails.

    Args:
        emails: list of email addresses
        do_smtp: whether to perform SMTP verification

    Returns:
        List of validation results (only valid emails)
    """
    # Deduplicate first (Step 3)
    unique_emails = list(set(e.strip().lower() for e in emails))

    tasks = [validate_email(e, do_smtp) for e in unique_emails]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid_results = []
    for r in results:
        if isinstance(r, dict) and r.get("valid"):
            valid_results.append(r)
        elif isinstance(r, Exception):
            logger.error("Validation error: %s", r)

    logger.info("Validated %d/%d emails as valid", len(valid_results), len(unique_emails))
    return valid_results
