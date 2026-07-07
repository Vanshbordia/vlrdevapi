from selectolax.parser import HTMLParser

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


def _get_buy_type(text: str) -> BuyType:
    """Convert buy type text to a BuyType enum value.

    Args:
        text: Raw buy type text ('' for eco, '$' for semi-eco, etc.).

    Returns:
        BuyType: Corresponding enum value.

    """
    text = text.strip()
    return _BUY_TYPE_MAP.get(text, BuyType.ECO)


def parse_economy_data(html: HTMLParser) -> EconomyData:
    """Parse economy data from the series page HTML.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        EconomyData: Parsed economy data with per-round team banks and
        spends.

    """
    econ_tables = html.css(".wf-table-inset.mod-econ")
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

        spent_team1 = int(sq1.attributes.get("title") or "0")
        spent_team2 = int(sq2.attributes.get("title") or "0")

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
