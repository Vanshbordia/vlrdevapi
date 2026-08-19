"""Shared utilities — datetime, country, prize, timezone, and region mappings."""

from vlrdevapi.commons.countries import COUNTRIES, get_country_name
from vlrdevapi.commons.datetime import (
    UTC,
    VLR_TIMEZONE,
    parse_vlr_date,
    parse_vlr_datetime,
    parse_vlr_iso_datetime,
    parse_vlr_time,
)
from vlrdevapi.commons.prizes import parse_prize_amount
from vlrdevapi.commons.regions import (
    COUNTRY_TO_REGION,
    SUBREGION_TO_REGION,
    VALID_REGIONS,
    resolve_country_to_region,
    resolve_subregion_to_region,
)
from vlrdevapi.commons.timezone import (
    REFERENCE_MATCH_PATH,
    VLR_STORED_TZ,
    detect_vlr_timezone,
    detect_vlr_timezone_from_url,
    parse_vlr_stored_datetime,
)

__all__ = [
    "COUNTRIES",
    "COUNTRY_TO_REGION",
    "REFERENCE_MATCH_PATH",
    "SUBREGION_TO_REGION",
    "UTC",
    "VALID_REGIONS",
    "VLR_STORED_TZ",
    "VLR_TIMEZONE",
    "detect_vlr_timezone",
    "detect_vlr_timezone_from_url",
    "get_country_name",
    "parse_prize_amount",
    "parse_vlr_date",
    "parse_vlr_datetime",
    "parse_vlr_iso_datetime",
    "parse_vlr_stored_datetime",
    "parse_vlr_time",
    "resolve_country_to_region",
    "resolve_subregion_to_region",
]
