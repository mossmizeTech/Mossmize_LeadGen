"""
Keyword Expansion Engine
Expands seed keywords into related niche search terms for broader coverage.
"""

# Pre-built synonym/expansion map for common business categories
KEYWORD_EXPANSIONS: dict[str, list[str]] = {
    # Healthcare
    "dentist": [
        "dentist", "dental clinic", "cosmetic dentist", "orthodontist",
        "pediatric dentist", "dental hospital", "dental surgeon",
        "teeth whitening", "dental implants", "endodontist",
    ],
    "doctor": [
        "doctor", "medical clinic", "hospital", "physician",
        "general practitioner", "health clinic", "medical center",
        "family doctor", "primary care", "urgent care",
    ],
    "physiotherapist": [
        "physiotherapist", "physiotherapy clinic", "physical therapy",
        "rehab center", "sports physiotherapy", "chiropractic",
    ],
    # Food & Hospitality
    "restaurant": [
        "restaurant", "cafe", "bistro", "diner", "eatery",
        "fine dining", "fast food", "food court", "buffet",
        "pizzeria", "sushi bar", "bakery",
    ],
    "hotel": [
        "hotel", "motel", "resort", "boutique hotel", "guest house",
        "bed and breakfast", "lodge", "inn", "hostel",
    ],
    # Professional Services
    "lawyer": [
        "lawyer", "law firm", "attorney", "legal services",
        "advocate", "legal consultant", "notary",
    ],
    "accountant": [
        "accountant", "accounting firm", "CPA", "tax consultant",
        "bookkeeper", "audit firm", "chartered accountant",
    ],
    "marketing agency": [
        "marketing agency", "digital marketing", "SEO agency",
        "advertising agency", "social media agency", "PR agency",
        "branding agency", "creative agency", "marketing consultant",
    ],
    # Technology
    "software company": [
        "software company", "software development", "IT company",
        "tech company", "web development", "app development",
        "IT services", "IT consulting", "SaaS company",
    ],
    # Real Estate
    "real estate": [
        "real estate agent", "real estate agency", "property dealer",
        "real estate broker", "property management", "real estate consultant",
    ],
    # Education
    "school": [
        "school", "high school", "primary school", "international school",
        "private school", "boarding school", "montessori school",
    ],
    "coaching": [
        "coaching center", "coaching institute", "tuition center",
        "tutorial", "test prep", "competitive exam coaching",
    ],
    # Fitness
    "gym": [
        "gym", "fitness center", "health club", "yoga studio",
        "crossfit", "pilates studio", "personal trainer",
    ],
    # Automotive
    "car repair": [
        "car repair", "auto repair", "mechanic", "car service center",
        "car workshop", "auto body shop", "car detailing",
    ],
    # Home Services
    "plumber": [
        "plumber", "plumbing services", "plumbing contractor",
        "emergency plumber", "pipe repair",
    ],
    "electrician": [
        "electrician", "electrical contractor", "electrical services",
        "wiring specialist", "electrical repair",
    ],
}


def expand_keywords(keywords: list[str]) -> list[str]:
    """
    Expand a list of seed keywords into a broader set of niche search terms.

    If a keyword matches a known category, its expansions are used.
    Unknown keywords are passed through as-is.

    Args:
        keywords: list of seed keywords (e.g. ["dentist", "restaurant"])

    Returns:
        Deduplicated list of expanded keywords
    """
    expanded: list[str] = []

    for kw in keywords:
        kw_lower = kw.strip().lower()
        if kw_lower in KEYWORD_EXPANSIONS:
            expanded.extend(KEYWORD_EXPANSIONS[kw_lower])
        else:
            # Pass through unknown keywords unchanged
            expanded.append(kw.strip())

    # Deduplicate while preserving order
    seen: set[str] = set()
    result: list[str] = []
    for term in expanded:
        term_lower = term.lower()
        if term_lower not in seen:
            seen.add(term_lower)
            result.append(term)

    return result
