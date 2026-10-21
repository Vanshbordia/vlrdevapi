from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._player.placements.models import PlayerPlacements
from vlrdevapi._player.placements.parser import parse_player_placements

_PLAYER_FIXTURES = FIXTURES_DIR / "player"


def _parse(player_dir: str) -> PlayerPlacements:
    player_id = int(player_dir.split("_")[0])
    if _LIVE:
        html = HTMLParser(live_fetch(f"/player/{player_id}"))
    else:
        path = _PLAYER_FIXTURES / player_dir / "overview.html"
        html = HTMLParser(path.read_text(encoding="utf-8"))
    return parse_player_placements(html, player_id)


class TestYuviPlacements:
    def test_total_and_count(self):
        result = _parse("46051_yuvi")

        assert result.player_id == 46051
        assert result.total_winnings == 5082
        assert result.total_winnings_currency == "$"
        assert len(result.placements) == 13

    def test_first_placement(self):
        placement = _parse("46051_yuvi").placements[0]

        assert placement.event_id == 2968
        assert placement.event_name == "Challengers 2026: South Asia Split 2"
        assert placement.year == 2026
        assert placement.stage == "Playoffs"
        assert placement.placement == "2nd"
        assert placement.prize_amount == 1042
        assert placement.prize_currency == "$"
        assert placement.team_name == "S8UL Esports"

    def test_multiple_placements_in_one_event(self):
        result = _parse("46051_yuvi")
        event_rows = [p for p in result.placements if p.event_id == 2746]

        assert len(event_rows) == 2
        assert {row.stage for row in event_rows} == {"Championship", "Qualifier #1"}
        assert {row.placement for row in event_rows} == {"2nd", "1st"}
        assert {row.prize_amount for row in event_rows} == {112, 78}
        assert all(row.team_name == "The Rad Syndicate" for row in event_rows)

    def test_placement_without_prize(self):
        result = _parse("46051_yuvi")
        placement = next(
            p for p in result.placements if p.event_id == 2624
        )

        assert placement.stage == "Main Event"
        assert placement.placement == "4th"
        assert placement.prize_amount is None
        assert placement.prize_currency is None
        assert placement.team_name == "The Rad Syndicate"


class TestOtherPlayers:
    def test_ethan_placements(self):
        result = _parse("11225_ethan")

        assert result.total_winnings == 645700
        assert result.total_winnings_currency == "$"
        assert len(result.placements) == 45
        assert result.placements[0].event_id == 2766
        assert result.placements[0].team_name == "NRG"

    def test_ethan_placement_without_prize(self):
        result = _parse("11225_ethan")
        placement = next(
            p
            for p in result.placements
            if p.event_id == 2977 and p.stage == "Group Stage"
        )

        assert placement.placement == "1st–2nd"
        assert placement.prize_amount is None
        assert placement.prize_currency is None

    def test_inspire_placements(self):
        result = _parse("53_inspire")

        assert result.total_winnings == 28450
        assert result.total_winnings_currency == "$"
        assert len(result.placements) == 27
        assert result.placements[0].event_id == 3127
        assert result.placements[0].placement == "5th–8th"
        assert result.placements[0].team_name == "Ascension Winners"
