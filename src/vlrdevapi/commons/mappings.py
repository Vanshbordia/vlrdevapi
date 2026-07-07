from typing import Literal

from vlrdevapi.exceptions import ValidationError

TIER_MAPPINGS: dict[str, str] = {
    "all": "",
    "vct": "60",
    "vcl": "61",
    "t3": "62",
    "gc": "63",
    "collegiate": "64",
    "offseason": "67",
}

REGION_MAPPINGS: dict[str, str] = {
    "all": "",
    "americas": "26",
    "amer": "26",
    "emea": "27",
    "pacific": "28",
    "pac": "28",
    "china": "24",
}

VALID_TIERS = list(TIER_MAPPINGS.keys())
VALID_REGIONS = list(REGION_MAPPINGS.keys())

# Type aliases for better IDE support
TierType = str
RegionType = str
StatusType = Literal["ongoing", "upcoming", "completed", "paused"]


def resolve_tier(tier: TierType) -> str:
    """Resolve tier parameter to URL value, case-insensitive."""
    tier_lower = tier.lower()
    if tier_lower not in TIER_MAPPINGS:
        msg = f"invalid tier '{tier}', valid options: {VALID_TIERS}"
        raise ValidationError(msg)
    return TIER_MAPPINGS[tier_lower]


def resolve_region(region: RegionType) -> str:
    """Resolve region parameter to URL value, case-insensitive."""
    region_lower = region.lower()
    if region_lower not in REGION_MAPPINGS:
        msg = f"invalid region '{region}', valid options: {VALID_REGIONS}"
        raise ValidationError(msg)
    return REGION_MAPPINGS[region_lower]
