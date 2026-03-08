"""
Global Regions Registry
Pre-built city lists for target countries/regions to enable automated multi-city searches.
"""

from typing import Optional


# ──────────────────────────────────────────────
# Supported regions and their major cities
# ──────────────────────────────────────────────

REGIONS: dict[str, dict[str, list[str]]] = {

    # ── North America ──
    "US": {
        "name": "United States",
        "cities": [
            "New York, NY, USA", "Los Angeles, CA, USA", "Chicago, IL, USA",
            "Houston, TX, USA", "Phoenix, AZ, USA", "Philadelphia, PA, USA",
            "San Antonio, TX, USA", "San Diego, CA, USA", "Dallas, TX, USA",
            "San Jose, CA, USA", "Austin, TX, USA", "Jacksonville, FL, USA",
            "Fort Worth, TX, USA", "Columbus, OH, USA", "Charlotte, NC, USA",
            "Indianapolis, IN, USA", "San Francisco, CA, USA", "Seattle, WA, USA",
            "Denver, CO, USA", "Nashville, TN, USA", "Washington, DC, USA",
            "Boston, MA, USA", "Las Vegas, NV, USA", "Portland, OR, USA",
            "Atlanta, GA, USA", "Miami, FL, USA", "Tampa, FL, USA",
            "Orlando, FL, USA", "Minneapolis, MN, USA", "Raleigh, NC, USA",
        ],
    },
    "CA": {
        "name": "Canada",
        "cities": [
            "Toronto, ON, Canada", "Montreal, QC, Canada", "Vancouver, BC, Canada",
            "Calgary, AB, Canada", "Edmonton, AB, Canada", "Ottawa, ON, Canada",
            "Winnipeg, MB, Canada", "Quebec City, QC, Canada", "Hamilton, ON, Canada",
            "Kitchener, ON, Canada", "Halifax, NS, Canada", "Victoria, BC, Canada",
            "London, ON, Canada", "Saskatoon, SK, Canada", "Regina, SK, Canada",
        ],
    },

    # ── Europe ──
    "GB": {
        "name": "United Kingdom",
        "cities": [
            "London, UK", "Manchester, UK", "Birmingham, UK", "Leeds, UK",
            "Glasgow, UK", "Liverpool, UK", "Edinburgh, UK", "Bristol, UK",
            "Sheffield, UK", "Newcastle, UK", "Cardiff, UK", "Belfast, UK",
            "Nottingham, UK", "Leicester, UK", "Brighton, UK",
        ],
    },
    "DE": {
        "name": "Germany",
        "cities": [
            "Berlin, Germany", "Hamburg, Germany", "Munich, Germany",
            "Cologne, Germany", "Frankfurt, Germany", "Stuttgart, Germany",
            "Düsseldorf, Germany", "Leipzig, Germany", "Dortmund, Germany",
            "Essen, Germany", "Bremen, Germany", "Dresden, Germany",
            "Hanover, Germany", "Nuremberg, Germany",
        ],
    },
    "FR": {
        "name": "France",
        "cities": [
            "Paris, France", "Marseille, France", "Lyon, France",
            "Toulouse, France", "Nice, France", "Nantes, France",
            "Strasbourg, France", "Montpellier, France", "Bordeaux, France",
            "Lille, France", "Rennes, France", "Reims, France",
        ],
    },
    "IT": {
        "name": "Italy",
        "cities": [
            "Rome, Italy", "Milan, Italy", "Naples, Italy", "Turin, Italy",
            "Palermo, Italy", "Genoa, Italy", "Bologna, Italy", "Florence, Italy",
            "Venice, Italy", "Verona, Italy", "Bari, Italy",
        ],
    },
    "ES": {
        "name": "Spain",
        "cities": [
            "Madrid, Spain", "Barcelona, Spain", "Valencia, Spain",
            "Seville, Spain", "Zaragoza, Spain", "Málaga, Spain",
            "Murcia, Spain", "Palma, Spain", "Bilbao, Spain",
        ],
    },
    "NL": {
        "name": "Netherlands",
        "cities": [
            "Amsterdam, Netherlands", "Rotterdam, Netherlands",
            "The Hague, Netherlands", "Utrecht, Netherlands",
            "Eindhoven, Netherlands", "Groningen, Netherlands",
        ],
    },
    "BE": {
        "name": "Belgium",
        "cities": [
            "Brussels, Belgium", "Antwerp, Belgium", "Ghent, Belgium",
            "Charleroi, Belgium", "Liège, Belgium", "Bruges, Belgium",
        ],
    },
    "SE": {
        "name": "Sweden",
        "cities": [
            "Stockholm, Sweden", "Gothenburg, Sweden", "Malmö, Sweden",
            "Uppsala, Sweden", "Linköping, Sweden",
        ],
    },
    "NO": {
        "name": "Norway",
        "cities": [
            "Oslo, Norway", "Bergen, Norway", "Stavanger, Norway",
            "Trondheim, Norway", "Drammen, Norway",
        ],
    },
    "DK": {
        "name": "Denmark",
        "cities": [
            "Copenhagen, Denmark", "Aarhus, Denmark", "Odense, Denmark",
            "Aalborg, Denmark",
        ],
    },
    "FI": {
        "name": "Finland",
        "cities": [
            "Helsinki, Finland", "Espoo, Finland", "Tampere, Finland",
            "Turku, Finland", "Oulu, Finland",
        ],
    },
    "PL": {
        "name": "Poland",
        "cities": [
            "Warsaw, Poland", "Kraków, Poland", "Wrocław, Poland",
            "Łódź, Poland", "Poznań, Poland", "Gdańsk, Poland",
        ],
    },
    "AT": {
        "name": "Austria",
        "cities": [
            "Vienna, Austria", "Graz, Austria", "Linz, Austria",
            "Salzburg, Austria", "Innsbruck, Austria",
        ],
    },
    "CH": {
        "name": "Switzerland",
        "cities": [
            "Zurich, Switzerland", "Geneva, Switzerland", "Basel, Switzerland",
            "Bern, Switzerland", "Lausanne, Switzerland",
        ],
    },
    "PT": {
        "name": "Portugal",
        "cities": [
            "Lisbon, Portugal", "Porto, Portugal", "Braga, Portugal",
            "Coimbra, Portugal", "Faro, Portugal",
        ],
    },
    "IE": {
        "name": "Ireland",
        "cities": [
            "Dublin, Ireland", "Cork, Ireland", "Galway, Ireland",
            "Limerick, Ireland",
        ],
    },
    "GR": {
        "name": "Greece",
        "cities": [
            "Athens, Greece", "Thessaloniki, Greece", "Patras, Greece",
            "Heraklion, Greece",
        ],
    },
    "CZ": {
        "name": "Czech Republic",
        "cities": [
            "Prague, Czech Republic", "Brno, Czech Republic",
            "Ostrava, Czech Republic", "Plzeň, Czech Republic",
        ],
    },
    "RO": {
        "name": "Romania",
        "cities": [
            "Bucharest, Romania", "Cluj-Napoca, Romania",
            "Timișoara, Romania", "Iași, Romania",
        ],
    },
    "HU": {
        "name": "Hungary",
        "cities": [
            "Budapest, Hungary", "Debrecen, Hungary", "Szeged, Hungary",
        ],
    },

    # ── Russia ──
    "RU": {
        "name": "Russia",
        "cities": [
            "Moscow, Russia", "Saint Petersburg, Russia",
            "Novosibirsk, Russia", "Yekaterinburg, Russia",
            "Kazan, Russia", "Nizhny Novgorod, Russia",
            "Chelyabinsk, Russia", "Samara, Russia",
            "Rostov-on-Don, Russia", "Krasnodar, Russia",
        ],
    },

    # ── Oceania ──
    "AU": {
        "name": "Australia",
        "cities": [
            "Sydney, NSW, Australia", "Melbourne, VIC, Australia",
            "Brisbane, QLD, Australia", "Perth, WA, Australia",
            "Adelaide, SA, Australia", "Gold Coast, QLD, Australia",
            "Canberra, ACT, Australia", "Hobart, TAS, Australia",
            "Darwin, NT, Australia", "Newcastle, NSW, Australia",
        ],
    },
    "NZ": {
        "name": "New Zealand",
        "cities": [
            "Auckland, New Zealand", "Wellington, New Zealand",
            "Christchurch, New Zealand", "Hamilton, New Zealand",
            "Dunedin, New Zealand", "Tauranga, New Zealand",
        ],
    },

    # ── Singapore ──
    "SG": {
        "name": "Singapore",
        "cities": [
            "Singapore",
        ],
    },

    # ── Gulf Countries ──
    "AE": {
        "name": "United Arab Emirates",
        "cities": [
            "Dubai, UAE", "Abu Dhabi, UAE", "Sharjah, UAE",
            "Ajman, UAE", "Ras Al Khaimah, UAE", "Fujairah, UAE",
        ],
    },
    "SA": {
        "name": "Saudi Arabia",
        "cities": [
            "Riyadh, Saudi Arabia", "Jeddah, Saudi Arabia",
            "Mecca, Saudi Arabia", "Medina, Saudi Arabia",
            "Dammam, Saudi Arabia", "Khobar, Saudi Arabia",
        ],
    },
    "KW": {
        "name": "Kuwait",
        "cities": [
            "Kuwait City, Kuwait", "Hawalli, Kuwait",
            "Salmiya, Kuwait", "Farwaniya, Kuwait",
        ],
    },
    "BH": {
        "name": "Bahrain",
        "cities": [
            "Manama, Bahrain", "Riffa, Bahrain", "Muharraq, Bahrain",
        ],
    },
    "QA": {
        "name": "Qatar",
        "cities": [
            "Doha, Qatar", "Al Wakrah, Qatar", "Al Khor, Qatar",
        ],
    },
    "OM": {
        "name": "Oman",
        "cities": [
            "Muscat, Oman", "Salalah, Oman", "Sohar, Oman",
        ],
    },
}

# Pre-built region groups for convenience
REGION_GROUPS: dict[str, list[str]] = {
    "north_america": ["US", "CA"],
    "europe": [
        "GB", "DE", "FR", "IT", "ES", "NL", "BE", "SE", "NO", "DK",
        "FI", "PL", "AT", "CH", "PT", "IE", "GR", "CZ", "RO", "HU",
    ],
    "russia": ["RU"],
    "oceania": ["AU", "NZ"],
    "gulf": ["AE", "SA", "KW", "BH", "QA", "OM"],
    "singapore": ["SG"],
    "all": list(REGIONS.keys()),
}


def get_cities_for_country(country_code: str) -> list[str]:
    """Get all cities for a country code (e.g. 'US')."""
    country = REGIONS.get(country_code.upper())
    if not country:
        return []
    return country["cities"]


def get_cities_for_region(region: str) -> list[str]:
    """Get all cities for a region group (e.g. 'europe', 'gulf')."""
    country_codes = REGION_GROUPS.get(region.lower(), [])
    cities = []
    for code in country_codes:
        cities.extend(get_cities_for_country(code))
    return cities


def get_all_supported_countries() -> list[dict]:
    """Return list of all supported countries with codes and city counts."""
    return [
        {
            "code": code,
            "name": data["name"],
            "city_count": len(data["cities"]),
        }
        for code, data in REGIONS.items()
    ]


def resolve_cities(
    city: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
) -> list[str]:
    """
    Resolve city list from various input types.

    Priority: city > country > region
    If city is given with country, appends country context for geocoding accuracy.

    Returns:
        List of city strings ready for geocoding
    """
    if city:
        # If country is also given, append it for geocoding accuracy
        if country and country.upper() in REGIONS:
            country_name = REGIONS[country.upper()]["name"]
            # Only append if not already present in the city string
            if country_name.lower() not in city.lower() and country.upper() not in city.upper():
                return [f"{city}, {country_name}"]
        return [city]

    if country:
        return get_cities_for_country(country)

    if region:
        return get_cities_for_region(region)

    return []
