"""Shared prize parsing utilities."""

import re


def parse_prize_amount(text: str) -> tuple[int | None, str | None]:
    """Extract numeric amount and currency symbol from a prize string.

    Examples:
        "$125,000" -> (125000, "$")
        "€50,000" -> (50000, "€")
        "" -> (None, None)
        "-" -> (None, None)

    """
    cleaned = text.strip()
    if not cleaned or cleaned == "-" or cleaned.upper() == "TBD":
        return None, None

    currency_match = re.match(r"^([^\d\s]+)", cleaned)
    currency_symbol = currency_match.group(1) if currency_match else None

    amount_match = re.search(r"[\d,]+", cleaned)
    if amount_match:
        try:
            amount = int(amount_match.group().replace(",", ""))
        except ValueError:
            pass
        else:
            return amount, currency_symbol

    return None, currency_symbol
