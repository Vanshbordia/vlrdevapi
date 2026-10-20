"""Series economy parser — extracts per-round bank and spend data."""

from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from vlrdevapi._series._utils import resolve_game_id
from vlrdevapi._series.economy.models import (
    BuyTierRecord,
    BuyType,
    EconomyData,
    EconScore,
    RoundEconomyData,
    RoundWinner,
)

# The "ecr" round grid encodes the buy level as a class on ``.ecc-sq``.
# ``mod-bp`` squares mark pistol rounds, while ``mod-b1``/``mod-b2``/
# ``mod-b3`` are eco (under 10k), half buy (10k-18k) and full buy (18k+).
# The inner ``ecc-q`` chip repeats the same tier as ``mod-q1``/``mod-q2``/
# ``mod-q3`` (pistol squares carry ``ecc-pm`` instead).
_BUY_CLASS_MAP: dict[str, BuyType] = {
    "mod-bp": BuyType.PISTOL,
    "mod-b1": BuyType.ECO,
    "mod-b2": BuyType.HALF_BUY,
    "mod-b3": BuyType.FULL_BUY,
}

# Summary-table step headers -> TeamBuyMatrix field names.
_PISTOL_STEP_KEYS: dict[str, str] = {
    "pistol": "pistol",
    "conv.": "converted",
    "converted": "converted",
    "bonus": "bonus",
}

# Tier-table group titles -> TeamBuyMatrix field names.
_TIER_KEYS: dict[str, str] = {
    "on eco": "on_eco",
    "on half buy": "on_half_buy",
    "on full buy": "on_full_buy",
}

# Buy-tier foot labels (``vs. Eco`` / ``vs. Half`` / ``vs. Full``) ->
# BuyTierRecord field names.
_VS_KEYS: dict[str, str] = {
    "eco": "vs_eco",
    "half": "vs_half",
    "full": "vs_full",
}

# Default column order when the foot row is missing or incomplete.
_DEFAULT_VS_ORDER: tuple[str, ...] = ("vs_eco", "vs_half", "vs_full")


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
    """Parse the VLR round-by-round ``.vlr-rounds.ecr`` grid.

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


def _normalize_label(text: str) -> str:
    """Collapse whitespace and casefold a label for matching."""
    return " ".join((text or "").split()).strip().casefold()


def _th_label(th: Node) -> str:
    """Team label from a matrix row header (title attribute, fallback text)."""
    title = (th.attributes.get("title") or "").strip()
    if title:
        return title
    return th.text(strip=True)


def _parse_matrix_score(td: Node | None) -> EconScore | None:
    """Parse a matrix ``won/total`` cell — ``None`` for empty (dash) cells."""
    if td is None:
        return None
    classes = (td.attributes.get("class") or "").split()
    if "mod-empty" in classes:
        return None
    score = td.css_first(".ecm-score")
    if score is None:
        return None
    text = " ".join(score.text(strip=True).split())
    won, sep, total = text.partition("/")
    if not sep:
        return None
    try:
        return EconScore(won=int(won.strip() or 0), total=int(total.strip() or 0))
    except ValueError:
        return None


def _parse_summary_table(table: Node) -> list[tuple[str, dict[str, EconScore]]]:
    """Parse the Pistol / Conv. / Bonus summary table.

    Returns ``(team_label, {matrix_field: score})`` per data row, in
    render order (team 1 first).
    """
    column_keys: list[str] = []
    rows: list[tuple[str, dict[str, EconScore]]] = []
    for tr in table.css("tr"):
        ths = tr.css("th")
        tds = tr.css("td")
        if ths and not tds:
            # Header row: read the step names in order (Pistol/Conv./Bonus).
            column_keys = [
                key
                for th in ths
                if (key := _PISTOL_STEP_KEYS.get(_normalize_label(th.text(strip=True))))
            ]
            continue
        if not tds:
            continue
        label = _th_label(ths[0]) if ths else ""
        fields: dict[str, EconScore] = {}
        for idx, td in enumerate(tds):
            if idx >= len(column_keys):
                break
            score = _parse_matrix_score(td)
            if score:
                fields[column_keys[idx]] = score
        rows.append((label, fields))
    return rows


def _parse_tier_table(table: Node) -> tuple[str | None, list[tuple[str, BuyTierRecord]]]:
    """Parse an ``On Eco`` / ``On Half buy`` / ``On Full buy`` tier table.

    Returns ``(tier_field, rows)`` where each row is
    ``(team_label_or_empty, BuyTierRecord)`` in render order.
    """
    tier_key: str | None = None
    group_title = table.css_first(".ecm-gt-t")
    if group_title is not None:
        for span in group_title.css("span"):
            if span is group_title:
                continue  # lexbor includes the matched node itself
            key = _TIER_KEYS.get(_normalize_label(span.text(strip=True)))
            if key:
                tier_key = key
                break
    if tier_key is None:
        return None, []

    # The foot row (``vs. Eco`` / ``vs. Half`` / ``vs. Full``) gives the
    # column meaning; fall back to VLR's standard order.
    foot_keys: list[str] = []
    for tr in table.css("tr"):
        foot_ths = [
            th
            for th in tr.css("th")
            if "ecm-foot" in (th.attributes.get("class") or "").split()
        ]
        if foot_ths:
            for th in foot_ths:
                label = _normalize_label(th.text(strip=True)).removeprefix("vs.").strip()
                key = _VS_KEYS.get(label)
                if key:
                    foot_keys.append(key)
            break

    rows: list[tuple[str, BuyTierRecord]] = []
    for tr in table.css("tr"):
        tds = tr.css("td")
        if not tds:
            continue  # header / foot rows
        ths = tr.css("th")
        label = ""
        if ths and "ecm-team-th" in (ths[0].attributes.get("class") or "").split():
            label = _th_label(ths[0])
        fields: dict[str, EconScore] = {}
        for idx, td in enumerate(tds):
            vs_key = (
                foot_keys[idx]
                if idx < len(foot_keys)
                else _DEFAULT_VS_ORDER[idx] if idx < len(_DEFAULT_VS_ORDER) else None
            )
            if vs_key is None:
                break
            score = _parse_matrix_score(td)
            if score:
                fields[vs_key] = score
        rows.append((label, BuyTierRecord(**fields)))
    return tier_key, rows


def _parse_buy_matrix(game_div: Node, economy: EconomyData) -> None:
    """Parse the ``.ecm-groups`` buy-type matrix into the economy result.

    Rows are matched to ``team1``/``team2`` by their header label; tables
    that render rows without headers (some tier tables) fall back to
    render order, which always lists team 1 first. Also fills the flat
    ``pistol_*`` / ``converted_*`` / ``bonus_*`` shortcuts from the
    matrices, and fills ``team1``/``team2`` tags from the matrix labels
    when the round grid did not provide them (e.g. the "All Maps"
    aggregate view).
    """
    groups = game_div.css_first(".ecm-groups")
    if groups is None:
        return

    entries: list[tuple[str, str, int, EconScore | BuyTierRecord]] = []
    label_order: list[str] = []
    label_seen: set[str] = set()

    def _collect(key: str, label: str, index: int, value: EconScore | BuyTierRecord) -> None:
        entries.append((key, label, index, value))
        norm = _normalize_label(label)
        if norm and norm not in label_seen:
            label_seen.add(norm)
            label_order.append(label)

    for table in groups.css("table.ecm"):
        if table.css_first(".ecm-gt-t") is not None:
            tier_key, rows = _parse_tier_table(table)
            if tier_key is None:
                continue
            for index, (label, record) in enumerate(rows):
                _collect(tier_key, label, index, record)
        else:
            for index, (label, fields) in enumerate(_parse_summary_table(table)):
                for key, score in fields.items():
                    _collect(key, label, index, score)

    def _team_for(label: str, index: int) -> str | None:
        norm = _normalize_label(label)
        if norm:
            if norm == _normalize_label(economy.team1):
                return "team1"
            if norm == _normalize_label(economy.team2):
                return "team2"
            norms = [_normalize_label(x) for x in label_order]
            if norms and norm == norms[0]:
                return "team1"
            if len(norms) > 1 and norm == norms[1]:
                return "team2"
            return None
        return "team1" if index == 0 else "team2" if index == 1 else None

    for key, label, index, value in entries:
        team = _team_for(label, index)
        if team == "team1":
            setattr(economy.buy_matrix_team1, key, value)
        elif team == "team2":
            setattr(economy.buy_matrix_team2, key, value)

    if not economy.team1 and label_order:
        economy.team1 = label_order[0]
    if not economy.team2 and len(label_order) > 1:
        economy.team2 = label_order[1]

    # Populate the flat summary shortcuts from the matrices.
    m1, m2 = economy.buy_matrix_team1, economy.buy_matrix_team2
    economy.pistol_team1 = m1.pistol
    economy.converted_team1 = m1.converted
    economy.bonus_team1 = m1.bonus
    economy.pistol_team2 = m2.pistol
    economy.converted_team2 = m2.converted
    economy.bonus_team2 = m2.bonus


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

    # VLR renders the round-by-round economy grid inside the game container.
    rounds_root = game_div.css_first(".vlr-rounds.ecr")
    economy = _parse_ecr_economy(rounds_root) if rounds_root else EconomyData()

    # The buy-type matrix sits next to the round grid; the "All Maps"
    # aggregate view has only the matrix (no round grid).
    _parse_buy_matrix(game_div, economy)
    return economy
