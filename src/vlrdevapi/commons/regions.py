"""Valorant competitive region, subregion, and country mappings.

Shared across event parsing, player/team region resolution, and any future
module that needs to resolve geographic data to Valorant competitive regions.

The 5 valid Valorant competitive regions:
  Americas, EMEA, Pacific, China, International
"""

# The 5 valid Valorant competitive regions
VALID_REGIONS: list[str] = ["Americas", "EMEA", "Pacific", "China", "International"]

# ---------------------------------------------------------------------------
# Subregion → parent region mapping
# Source: VLR.gg VCL 2025/2026 + Game Changers 2026 filter dropdowns
# ---------------------------------------------------------------------------

SUBREGION_TO_REGION: dict[str, str] = {
    # Americas (5)
    "North America": "Americas",
    "Brazil": "Americas",
    "LATAM North": "Americas",
    "LATAM South": "Americas",
    "LATAM": "Americas",
    # EMEA (7)
    "France": "EMEA",
    "DACH": "EMEA",
    "Spain": "EMEA",
    "NORTH//EAST": "EMEA",
    "Türkiye": "EMEA",
    "Turkey": "EMEA",
    "MENA": "EMEA",
    # Pacific (5)
    "Korea": "Pacific",
    "Japan": "Pacific",
    "Southeast Asia": "Pacific",
    "South Asia": "Pacific",
    "Oceania": "Pacific",
}

# ---------------------------------------------------------------------------
# Country name → Valorant competitive region
# Used as fallback when breadcrumb has no region= but region_location has a flag.
# Source: VLR.gg rankings + VCL subregion qualifier circuits
# ---------------------------------------------------------------------------

COUNTRY_TO_REGION: dict[str, str] = {
    # ── Pacific ──
    "Japan": "Pacific",
    "South Korea": "Pacific",
    "Thailand": "Pacific",
    "Vietnam": "Pacific",
    "Malaysia": "Pacific",
    "Singapore": "Pacific",
    "Philippines": "Pacific",
    "Indonesia": "Pacific",
    "Hong Kong": "Pacific",
    "Taiwan": "Pacific",
    "Myanmar": "Pacific",
    "Cambodia": "Pacific",
    "Laos": "Pacific",
    "Brunei": "Pacific",
    "India": "Pacific",
    "Nepal": "Pacific",
    "Bangladesh": "Pacific",
    "Sri Lanka": "Pacific",
    "Maldives": "Pacific",
    "Bhutan": "Pacific",
    "Australia": "Pacific",
    "New Zealand": "Pacific",
    "Fiji": "Pacific",
    "Papua New Guinea": "Pacific",
    "Samoa": "Pacific",
    "Tonga": "Pacific",
    "Solomon Islands": "Pacific",
    "Guam": "Pacific",
    "New Caledonia": "Pacific",
    "French Polynesia": "Pacific",
    # ── Americas ──
    "United States": "Americas",
    "Canada": "Americas",
    "Mexico": "Americas",
    "Brazil": "Americas",
    "Argentina": "Americas",
    "Chile": "Americas",
    "Colombia": "Americas",
    "Peru": "Americas",
    "Ecuador": "Americas",
    "Venezuela": "Americas",
    "Bolivia": "Americas",
    "Paraguay": "Americas",
    "Uruguay": "Americas",
    "Costa Rica": "Americas",
    "Cuba": "Americas",
    "Dominican Republic": "Americas",
    "El Salvador": "Americas",
    "Guatemala": "Americas",
    "Haiti": "Americas",
    "Honduras": "Americas",
    "Nicaragua": "Americas",
    "Panama": "Americas",
    "Puerto Rico": "Americas",
    "Trinidad and Tobago": "Americas",
    "Jamaica": "Americas",
    "Guyana": "Americas",
    "Suriname": "Americas",
    "Belize": "Americas",
    "Bahamas": "Americas",
    "Barbados": "Americas",
    "Guadeloupe": "Americas",
    "Martinique": "Americas",
    "Aruba": "Americas",
    "Cayman Islands": "Americas",
    "Turks and Caicos Islands": "Americas",
    "U.S. Virgin Islands": "Americas",
    "British Virgin Islands": "Americas",
    "Montserrat": "Americas",
    "Saint Lucia": "Americas",
    "Saint Pierre and Miquelon": "Americas",
    "Bermuda": "Americas",
    "Greenland": "Americas",
    "Netherlands Antilles": "Americas",
    "Sint Maarten": "Americas",
    # ── EMEA ──
    "Germany": "EMEA",
    "United Kingdom": "EMEA",
    "England": "EMEA",
    "Wales": "EMEA",
    "France": "EMEA",
    "Spain": "EMEA",
    "Italy": "EMEA",
    "Portugal": "EMEA",
    "Netherlands": "EMEA",
    "Belgium": "EMEA",
    "Sweden": "EMEA",
    "Norway": "EMEA",
    "Denmark": "EMEA",
    "Finland": "EMEA",
    "Poland": "EMEA",
    "Czech Republic": "EMEA",
    "Austria": "EMEA",
    "Switzerland": "EMEA",
    "Ireland": "EMEA",
    "Iceland": "EMEA",
    "Greece": "EMEA",
    "Hungary": "EMEA",
    "Romania": "EMEA",
    "Bulgaria": "EMEA",
    "Croatia": "EMEA",
    "Serbia": "EMEA",
    "Slovakia": "EMEA",
    "Slovenia": "EMEA",
    "Estonia": "EMEA",
    "Latvia": "EMEA",
    "Lithuania": "EMEA",
    "Malta": "EMEA",
    "Cyprus": "EMEA",
    "Luxembourg": "EMEA",
    "Monaco": "EMEA",
    "Andorra": "EMEA",
    "Montenegro": "EMEA",
    "North Macedonia": "EMEA",
    "Albania": "EMEA",
    "Bosnia and Herzegovina": "EMEA",
    "Kosovo": "EMEA",
    "Moldova": "EMEA",
    "Ukraine": "EMEA",
    "Georgia": "EMEA",
    "Faroe Islands": "EMEA",
    "Gibraltar": "EMEA",
    "Liechtenstein": "EMEA",
    "San Marino": "EMEA",
    "Vatican City": "EMEA",
    "Turkey": "EMEA",
    "Israel": "EMEA",
    "Lebanon": "EMEA",
    "Jordan": "EMEA",
    "Palestine": "EMEA",
    "Syria": "EMEA",
    "Iraq": "EMEA",
    "Iran": "EMEA",
    "Afghanistan": "EMEA",
    "Pakistan": "EMEA",
    "Saudi Arabia": "EMEA",
    "United Arab Emirates": "EMEA",
    "Qatar": "EMEA",
    "Bahrain": "EMEA",
    "Kuwait": "EMEA",
    "Oman": "EMEA",
    "Egypt": "EMEA",
    "Morocco": "EMEA",
    "Tunisia": "EMEA",
    "Algeria": "EMEA",
    "Libya": "EMEA",
    "Sudan": "EMEA",
    "Senegal": "EMEA",
    "Nigeria": "EMEA",
    "Ghana": "EMEA",
    "Kenya": "EMEA",
    "South Africa": "EMEA",
    "Russia": "EMEA",
    "Belarus": "EMEA",
    "Armenia": "EMEA",
    "Azerbaijan": "EMEA",
    "Kazakhstan": "EMEA",
    "Kyrgyzstan": "EMEA",
    "Tajikistan": "EMEA",
    "Turkmenistan": "EMEA",
    "Uzbekistan": "EMEA",
    "European Union": "EMEA",
    # ── China ──
    "China": "China",
    "Macau": "China",
}


def resolve_subregion_to_region(subregion_name: str) -> str | None:
    """Map a subregion name to its parent Valorant competitive region.

    Args:
        subregion_name: The subregion display name from vlr.gg breadcrumb
            (e.g. ``'Japan'``, ``'LATAM North'``, ``'NORTH//EAST'``).

    Returns:
        The parent region name, or ``None`` if the subregion is not recognized.

    """
    return SUBREGION_TO_REGION.get(subregion_name)


def resolve_country_to_region(country_name: str) -> str | None:
    """Map a country name to its Valorant competitive region.

    Args:
        country_name: Full country name (e.g. ``'Japan'``, ``'Germany'``,
            ``'Brazil'``).

    Returns:
        The Valorant region name, or ``None`` if the country is not recognized.

    """
    return COUNTRY_TO_REGION.get(country_name)
