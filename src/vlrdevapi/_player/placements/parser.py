import re

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from vlrdevapi._player._common_parsing import (
    _next_sibling_card,
    _parse_total_winnings,
)
from vlrdevapi._player.placements.models import (
    PlayerEventPlacement,
    PlayerPlacements,
)
from vlrdevapi._utils.text import normalize_whitespace
from vlrdevapi.commons.prizes import parse_prize_amount

_DASHES = ("\u2013", "\u2014", "\u2212", "-")


def parse_player_placements(
    html: HTMLParser,
    player_id: int,
) -> PlayerPlacements:
    """Parse event placements from a player overview page.

    Args:
        html: Parsed HTML of the player page.
        player_id: The player identifier.

    Returns:
        PlayerPlacements: Placements with total winnings.

    """
    result = PlayerPlacements(player_id=player_id)
    result.total_winnings, result.total_winnings_currency = _parse_total_winnings(html)

    placements_h2 = next(
        (
            h2
            for h2 in html.css("h2.wf-label.mod-large")
            if "Event Placements" in h2.text(strip=True)
        ),
        None,
    )
    if not placements_h2:
        return result

    card = _next_sibling_card(placements_h2)
    if not card:
        return result

    for event_link in card.css("a.player-event-item"):
        event_id = _parse_event_id(event_link)
        if event_id == 0:
            continue

        event_name = ""
        name_el = event_link.css_first(".text-of")
        if name_el:
            event_name = normalize_whitespace(name_el.text(strip=True))

        year = _parse_year(event_link)

        for group in event_link.css("div[style*='margin-top: 5px']"):
            placement = _parse_placement_group(
                group,
                event_id=event_id,
                event_name=event_name,
                year=year,
            )
            if placement:
                result.placements.append(placement)

    return result


def _parse_event_id(item: Node) -> int:
    href = item.attributes.get("href", "") or ""
    match = re.search(r"/event/(\d+)", href)
    return int(match.group(1)) if match else 0


def _parse_year(item: Node) -> int:
    for div in item.css("div"):
        text = div.text(strip=True)
        if re.fullmatch(r"\d{4}", text):
            return int(text)
    return 0


def _parse_placement_group(
    group: Node,
    *,
    event_id: int,
    event_name: str,
    year: int,
) -> PlayerEventPlacement | None:
    stage_el = group.css_first(".ge-text-light")
    stage, placement = _split_stage_and_placement(
        stage_el.text(strip=True) if stage_el else "",
    )
    if not stage and not placement:
        return None

    prize_el = group.css_first("span[style*='font-weight: 700']")
    prize_amount = None
    prize_currency = None
    if prize_el:
        prize_amount, prize_currency = parse_prize_amount(
            prize_el.text(strip=True),
        )

    raw_team = group.text()
    if stage_el:
        raw_team = raw_team.replace(stage_el.text(), "", 1)
    if prize_el:
        raw_team = raw_team.replace(prize_el.text(), "", 1)

    return PlayerEventPlacement(
        event_id=event_id,
        event_name=event_name,
        year=year,
        stage=stage,
        placement=placement,
        prize_amount=prize_amount,
        prize_currency=prize_currency,
        team_name=normalize_whitespace(raw_team),
    )


def _split_stage_and_placement(text: str) -> tuple[str, str]:
    normalized = normalize_whitespace(text)
    if not normalized:
        return "", ""

    for dash in _DASHES:
        if dash not in normalized:
            continue
        left, right = normalized.split(dash, 1)
        left = normalize_whitespace(left)
        right = normalize_whitespace(right)
        # A bare placement range such as "5th–6th" has no stage.
        if left[:1].isdigit() and right[:1].isdigit():
            return "", normalized
        return left, right

    return "", normalized
