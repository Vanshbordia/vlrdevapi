"""Series economy parser — extracts per-round bank and spend data."""

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from vlrdevapi._series._utils import resolve_game_id
from vlrdevapi._series.economy.models import (
    BuyType,
    EconomyData,
    RoundEconomyData,
    RoundWinner,
)

_BUY_TYPE_MAP: dict[str, BuyType] = {
    "": BuyType.ECO,
    "$": BuyType.SEMI_ECO,
    "$$": BuyType.SEMI_BUY,
    "$$$": BuyType.FULL_BUY,
}

# Newer "ecr" round grid encodes the buy level as a class on ``.ecc-sq``.
_BUY_CLASS_MAP: dict[str, BuyType] = {
    "mod-bp": BuyType.ECO,  # pistol round
    "mod-b1": BuyType.SEMI_ECO,
    "mod-b2": BuyType.SEMI_BUY,
    "mod-b3": BuyType.FULL_BUY,
}


def _get_buy_type(text: str) -> BuyType:
    """Convert buy type text to a BuyType enum value.

    Args:
        text: Raw buy type text ('' for eco, '$' for semi-eco, etc.).

    Returns:
        BuyType: Corresponding enum value.

    """
    text = text.strip()
    return _BUY_TYPE_MAP.get(text, BuyType.ECO)


def _get_ecr_buy_type(sq: Node | None) -> BuyType:
    """Resolve the buy type from an ``.ecc-sq`` round square's classes.

    Args:
        sq: The ``.ecc-sq`` node, or ``None``.

    Returns:
        BuyType: Corresponding enum value (defaults to eco).

    """
    if sq is None:
        return BuyType.ECO
    classes = (sq.attributes.get("class") or "").split()
    for cls in classes:
        if cls in _BUY_CLASS_MAP:
            return _BUY_CLASS_MAP[cls]
    return BuyType.ECO


def _parse_spend_k(title: str | None) -> int:
    """Parse a spend value from an ``.ecc-c`` title (e.g. ``'4.1k'``).

    Args:
        title: The title attribute text.

    Returns:
        int: Spend in credits, or ``0`` when absent/unparseable.

    """
    text = (title or "").strip().lower()
    if not text:
        return 0
    multiplier = 1000 if text.endswith("k") else 1
    if multiplier == 1000:
        text = text[:-1]
    try:
        return round(float(text) * multiplier)
    except ValueError:
        return 0


def _parse_bank_fig(text: str) -> float:
    """Parse a bank figure from an ``.ecr-fig`` (in thousands).

    Args:
        text: The figure text (e.g. ``'10.3'``).

    Returns:
        float: Bank in credits, or ``0.0`` when unparseable.

    """
    try:
        return float(text.strip()) * 1000
    except ValueError:
        return 0.0


def _parse_ecr_economy(rounds_root: Node) -> EconomyData:
    """Parse the newer VLR round-by-round ``.vlr-rounds.ecr`` grid.

    Args:
        rounds_root: The ``.vlr-rounds.ecr`` node.

    Returns:
        EconomyData: Parsed economy data with per-round bank, spend,
        buy type, and winner information.

    """
    teams_col = rounds_root.css_first(".vlr-rounds-row-col.mod-teams")
    tag_els = teams_col.css(".team .vlr-rounds-tag") if teams_col else []
    team1 = tag_els[0].text(strip=True) if len(tag_els) > 0 else ""
    team2 = tag_els[1].text(strip=True) if len(tag_els) > 1 else ""

    economy_data = EconomyData(team1=team1, team2=team2)

    round_number = 0
    for col in rounds_root.css(".vlr-rounds-row-col"):
        if "mod-teams" in (col.attributes.get("class") or ""):
            continue

        ecc1 = col.css_first(".ecc-c.mod-t1")
        ecc2 = col.css_first(".ecc-c.mod-t2")
        if ecc1 is None and ecc2 is None:
            continue

        # Unplayed rounds render empty cells (no title) — skip them.
        if not (ecc1.attributes.get("title") if ecc1 else None) and not (
            ecc2.attributes.get("title") if ecc2 else None
        ):
            continue

        round_number += 1

        bank1 = col.css_first(".ecr-bank.mod-t1 .ecr-fig")
        bank2 = col.css_first(".ecr-bank.mod-t2 .ecr-fig")

        sq1 = ecc1.css_first(".ecc-sq") if ecc1 else None
        sq2 = ecc2.css_first(".ecc-sq") if ecc2 else None

        winner_team = ""
        if sq1 and "mod-win" in (sq1.attributes.get("class") or "").split():
            winner_team = "team1"
        elif sq2 and "mod-win" in (sq2.attributes.get("class") or "").split():
            winner_team = "team2"

        round_data = RoundEconomyData(
            round_number=round_number,
            bank_team1=_parse_bank_fig(bank1.text(strip=True)) if bank1 else 0.0,
            bank_team2=_parse_bank_fig(bank2.text(strip=True)) if bank2 else 0.0,
            spent_team1=_parse_spend_k(ecc1.attributes.get("title") if ecc1 else None),
            spent_team2=_parse_spend_k(ecc2.attributes.get("title") if ecc2 else None),
            winner=RoundWinner(),
            buy_type_team1=_get_ecr_buy_type(sq1),
            buy_type_team2=_get_ecr_buy_type(sq2),
            is_pistol_round=round_number in (1, 13),
        )
        round_data._temp_winner = winner_team

        economy_data.rounds.append(round_data)

    return economy_data


def parse_economy_data(html: HTMLParser, game_id: int | str = "all") -> EconomyData:
    """Parse economy data from the series page HTML.

    Args:
        html: The selectolax HTMLParser of the series page.
        game_id: Game number within the series (1-based), or a real VLR
            game ID ("all" for the combined overview).

    Returns:
        EconomyData: Parsed economy data with per-round team banks and
        spends.

    """
    gid = resolve_game_id(html, game_id)
    game_div = html.css_first(f'.vm-stats-game[data-game-id="{gid}"]')
    if not game_div:
        return EconomyData()

    # Newer VLR layout renders the round-by-round economy grid directly.
    rounds_root = game_div.css_first(".vlr-rounds.ecr")
    if rounds_root:
        return _parse_ecr_economy(rounds_root)

    econ_tables = game_div.css(".wf-table-inset.mod-econ")
    if not econ_tables:
        return EconomyData()

    # Find the table that has both teams and round data
    econ_table = None
    for table in econ_tables:
        team_divs = table.css(".team")
        round_nums = table.css(".round-num")
        if len(team_divs) >= 2 and len(round_nums) > 0:
            econ_table = table
            break

    if not econ_table:
        return EconomyData()

    # Get teams
    team_divs = econ_table.css(".team")
    team1 = team_divs[0].text(strip=True)
    team2 = team_divs[1].text(strip=True)

    economy_data = EconomyData(team1=team1, team2=team2)

    # Parse each round
    for td in econ_table.css("td"):
        round_num_elem = td.css_first(".round-num")
        if not round_num_elem:
            continue

        try:
            round_number = int(round_num_elem.text(strip=True))
        except ValueError:
            continue

        # Get banks - first is team1, second is team2
        bank_elems = td.css(".bank")
        if len(bank_elems) < 2:
            continue

        try:
            bank_team1 = float(bank_elems[0].text(strip=True).replace("k", "")) * 1000
            bank_team2 = float(bank_elems[1].text(strip=True).replace("k", "")) * 1000
        except (ValueError, IndexError):
            continue

        # Get round squares
        rnd_sqs = td.css(".rnd-sq")
        if len(rnd_sqs) < 2:
            continue

        sq1 = rnd_sqs[0]  # team1
        sq2 = rnd_sqs[1]  # team2

        try:
            spent_team1 = int(sq1.attributes.get("title") or "0")
            spent_team2 = int(sq2.attributes.get("title") or "0")
        except ValueError:
            continue

        buy_type_team1 = _get_buy_type(sq1.text(strip=True))
        buy_type_team2 = _get_buy_type(sq2.text(strip=True))

        # Determine winner - will be set later in namespace
        winner_team = ""
        if "mod-win" in (sq1.attributes.get("class") or ""):
            winner_team = "team1"
        elif "mod-win" in (sq2.attributes.get("class") or ""):
            winner_team = "team2"

        is_pistol_round = round_number in [1, 13]

        round_data = RoundEconomyData(
            round_number=round_number,
            bank_team1=bank_team1,
            bank_team2=bank_team2,
            spent_team1=spent_team1,
            spent_team2=spent_team2,
            winner=RoundWinner(),  # Will be set later
            buy_type_team1=buy_type_team1,
            buy_type_team2=buy_type_team2,
            is_pistol_round=is_pistol_round,
        )

        # Store temporary winner info for later processing
        round_data._temp_winner = winner_team

        economy_data.rounds.append(round_data)

    # Sort rounds by round_number
    economy_data.rounds.sort(key=lambda r: r.round_number)

    return economy_data
