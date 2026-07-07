from selectolax.parser import HTMLParser

from vlrdevapi._player._common_parsing import _next_sibling_card, _parse_team_entry
from vlrdevapi._player.teams.models import PlayerTeams


def parse_player_teams(html: HTMLParser) -> PlayerTeams:
    result = PlayerTeams()

    labels = html.css("h2.wf-label.mod-large")
    for label in labels:
        text = label.text(strip=True)
        card = _next_sibling_card(label)
        if card is None:
            continue

        if text == "Current Teams":
            for a in card.css("a.wf-module-item"):
                result.current_teams.append(_parse_team_entry(a))
        elif text == "Past Teams":
            for a in card.css("a.wf-module-item"):
                result.past_teams.append(_parse_team_entry(a))

    return result
