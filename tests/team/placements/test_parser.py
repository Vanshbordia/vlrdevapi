import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._team.placements.parser import parse_team_placements


def _load_html(team_id: int) -> HTMLParser:
    path = (
        FIXTURES_DIR
        / "team"
        / str(team_id)
        / "overview_light.html"
    )
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseTeamPlacements:
    def test_parse_nrg_placements(self):
        html = _load_html(1034)
        result = parse_team_placements(html, 1034)

        assert result.team_id == 1034
        assert result.total_winnings == 1585375
        assert result.total_winnings_currency == "$"
        assert len(result.placements) > 0

    def test_parse_event_with_single_placement(self):
        html = _load_html(1034)
        result = parse_team_placements(html, 1034)

        valorant_champions = next(
            (p for p in result.placements if p.event_id == 2283), None
        )
        assert valorant_champions is not None
        assert valorant_champions.event_name == "Valorant Champions 2025"
        assert valorant_champions.year == 2025
        assert len(valorant_champions.placements) == 1
        assert valorant_champions.prize == 1000000
        assert valorant_champions.prize_currency == "$"

        placement = valorant_champions.placements[0]
        assert placement.stage == "Playoffs"
        assert placement.placement == "1st"

    def test_parse_event_with_multiple_placements(self):
        html = _load_html(1034)
        result = parse_team_placements(html, 1034)

        masters_tokyo = next((p for p in result.placements if p.event_id == 1494), None)
        assert masters_tokyo is not None
        assert masters_tokyo.event_name == "Champions Tour 2023: Masters Tokyo"
        assert masters_tokyo.year == 2023
        assert len(masters_tokyo.placements) == 2
        assert masters_tokyo.prize == 75000
        assert masters_tokyo.prize_currency == "$"

        group_stage = next(
            (p for p in masters_tokyo.placements if p.stage == "Group Stage"), None
        )
        assert group_stage is not None
        assert group_stage.placement == "1st–2nd"

        playoffs = next(
            (p for p in masters_tokyo.placements if p.stage == "Playoffs"), None
        )
        assert playoffs is not None
        assert playoffs.placement == "4th"

    def test_parse_event_without_prize(self):
        html = _load_html(1034)
        result = parse_team_placements(html, 1034)

        kickoff = next((p for p in result.placements if p.event_id == 2682), None)
        assert kickoff is not None
        assert kickoff.event_name == "VCT 2026: Americas Kickoff"
        assert len(kickoff.placements) == 1
        assert kickoff.prize is None
        assert kickoff.prize_currency is None

        placement = kickoff.placements[0]
        assert placement.stage == "Main Event"
        assert placement.placement == "3rd"

    def test_parse_placement_with_range(self):
        html = _load_html(1034)
        result = parse_team_placements(html, 1034)

        stage1 = next((p for p in result.placements if p.event_id == 2004), None)
        assert stage1 is not None
        assert len(stage1.placements) == 1

        placement = stage1.placements[0]
        assert placement.placement == "9th–10th"

    def test_parse_team_with_zero_winnings(self):
        html = _load_html(17676)
        result = parse_team_placements(html, 17676)

        assert result.team_id == 17676
        assert result.total_winnings == 0
        assert result.total_winnings_currency == "$"
        assert len(result.placements) >= 1

        first_event = result.placements[0]
        assert first_event.event_id == 2366
        assert first_event.event_name == "Challengers 2025: South Asia Stage 1"
        assert first_event.year == 2025

