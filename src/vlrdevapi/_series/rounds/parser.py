from selectolax.parser import HTMLParser

from vlrdevapi._series.rounds.models import RoundData, RoundsData, RoundWinType


def parse_rounds_data(html: HTMLParser) -> RoundsData:
    """Parse round-by-round data from the series page HTML.

    Args:
        html: The selectolax HTMLParser of the series page.

    Returns:
        RoundsData: Parsed round data with team names and per-round
        results.

    """
    rounds_container = html.css_first(".vlr-rounds")
    if not rounds_container:
        return RoundsData()

    # Get teams from first row
    first_row = rounds_container.css_first(".vlr-rounds-row")
    if not first_row:
        return RoundsData()

    teams = first_row.css(".team")
    if len(teams) < 2:
        return RoundsData()

    team1 = teams[0].text(strip=True)
    team2 = teams[1].text(strip=True)

    rounds_data = RoundsData(team1=team1, team2=team2)

    # Now parse all rounds
    for row in rounds_container.css(".vlr-rounds-row"):
        for col in row.css(".vlr-rounds-row-col:has(.rnd-num)"):
            title = (col.attributes.get("title", "") or "")
            if not title or "-" not in title:
                continue

            try:
                team1_score, team2_score = map(int, title.split("-"))
            except ValueError:
                continue

            rnd_num_elem = col.css_first(".rnd-num")
            if not rnd_num_elem:
                continue

            round_number = int(rnd_num_elem.text(strip=True))

            sqs = col.css(".rnd-sq")
            if len(sqs) != 2:
                continue

            win_sq = None
            winner_index = -1
            for i, sq in enumerate(sqs):
                classes = (sq.attributes.get("class", "") or "")
                if "mod-win" in classes:
                    win_sq = sq
                    winner_index = i
                    break

            if win_sq is None:
                continue

            winner_team_name = team1 if winner_index == 0 else team2

            # Determine actual side from mod-ct (Defense) / mod-t (Attack) class
            win_classes = (win_sq.attributes.get("class", "") or "")
            if "mod-ct" in win_classes:
                side = "Defense"
            elif "mod-t" in win_classes:
                side = "Attack"
            else:
                side = "Defense" if winner_index == 0 else "Attack"

            img = win_sq.css_first("img")
            win_type_str = "elim"  # default
            if img:
                src = (img.attributes.get("src", "") or "")
                if "/img/vlr/game/round/" in src and src.endswith(".webp"):
                    win_type_str = src.split("/")[-1].replace(".webp", "")

            try:
                win_type_enum = RoundWinType(win_type_str)
                win_type = win_type_enum.full_name
            except ValueError:
                win_type = "Elimination"  # fallback

            round_data = RoundData(
                round_number=round_number,
                winner_team_name=winner_team_name,
                winner_team_id=0,  # will be set later
                win_type=win_type,
                side=side,
                team1_score=team1_score,
                team2_score=team2_score,
            )

            rounds_data.rounds.append(round_data)

    # Sort rounds by round_number
    rounds_data.rounds.sort(key=lambda r: r.round_number)

    return rounds_data
