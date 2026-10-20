"""Shared text-normalization helpers for vlr.gg parsers."""

import re

_SDOT = "\u22c5"


def normalize_whitespace(text: str) -> str:
    """Collapse all whitespace (spaces, tabs, newlines) and strip.

    Parsers extract text from HTML that is heavily indented. Calling
    ``text(strip=True)`` removes the leading/trailing whitespace but leaves
    internal runs of tabs and newlines intact (for example
    ``"Playoffs \u22c5\\n\\t\\t\\tLBF"``). This helper makes the value stable
    for comparisons, serialization, and display.

    Args:
        text: Raw text extracted from an HTML node.

    Returns:
        Text with every whitespace run collapsed to a single space.

    """
    return re.sub(r"\s+", " ", text).strip()


def split_stage_bracket(text: str) -> tuple[str, str]:
    """Split a VLR stage/bracket label into its two parts.

    VLR renders labels either as ``"Playoffs \u22c5 LBF"`` (stage and bracket)
    or as a bare round such as ``"Ro16"`` (bracket only). Whitespace is
    normalized before splitting.

    Args:
        text: Raw stage/bracket label.

    Returns:
        ``(stage, bracket)``. When no ``\u22c5`` separator is present, the
        whole label is the bracket and the stage is empty.

    """
    normalized = normalize_whitespace(text)
    if not normalized:
        return "", ""

    if _SDOT in normalized:
        stage, bracket = normalized.split(_SDOT, 1)
        return stage.strip(), bracket.strip()

    return "", normalized
