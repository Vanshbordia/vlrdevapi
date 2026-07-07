"""Shared utilities for event namespaces."""


def _filter_stages(
    stages: list[tuple[str, str]], stage_filter: str | None,
) -> list[tuple[str, str]]:
    """Filter stages list by an optional substring match."""
    if not stage_filter:
        return stages
    stage_lower = stage_filter.lower()
    return [
        (href, name)
        for href, name in stages
        if stage_lower in href.lower() or stage_lower in name.lower()
    ]
