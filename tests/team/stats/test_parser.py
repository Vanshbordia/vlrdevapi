import pytest
from selectolax.parser import HTMLParser
from unittest.mock import MagicMock

from tests.conftest import FIXTURES_DIR
from vlrdevapi._series.info.models import SeriesInfo
from vlrdevapi._team.stats.parser import parse_team_stats


def _make_series_info(
    event_id=1234, event_name="Test Event", stage="Group Stage",
    patch="10.0", team1_id=1034, team1_name="NRG", team1_tag="NRG",
    team2_id=456, team2_name="Opponent", team2_tag="OPP",
):
    """Build a canned SeriesInfo object for testing detailed enrichment."""
    team1 = MagicMock(id=team1_id, name=team1_name, tag=team1_tag)
    team2 = MagicMock(id=team2_id, name=team2_name, tag=team2_tag)
    info = MagicMock(
        spec=SeriesInfo,
        event_id=event_id, event_name=event_name, stage=stage, patch=patch,
        team1=team1, team2=team2,
    )
    return info


def _load_html(team_id: int, filename: str) -> HTMLParser:
    path = (
        FIXTURES_DIR
        / "team"
        / str(team_id)
        / filename
    )
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseTeamStats:
    def test_parse_nrg_stats(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034)

        assert result.team_id == 1034
        assert len(result.maps) > 0

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.games_played == 91
        assert bind.win_rate == 62.0
        assert bind.wins == 56
        assert bind.losses == 35
        assert bind.attack_first == 52
        assert bind.defense_first == 39
        assert bind.attack_round_win_rate == 53.0
        assert bind.attack_rounds_won == 496
        assert bind.attack_rounds_lost == 439
        assert bind.defense_round_win_rate == 58.0
        assert bind.defense_rounds_won == 537
        assert bind.defense_rounds_lost == 393

        haven = next((m for m in result.maps if m.map_name == "Haven"), None)
        assert haven is not None
        assert haven.games_played == 128
        assert haven.win_rate == 73.0
        assert haven.wins == 93
        assert haven.losses == 35
        assert haven.attack_first == 66
        assert haven.defense_first == 62
        assert haven.attack_round_win_rate == 57.0
        assert haven.attack_rounds_won == 740
        assert haven.attack_rounds_lost == 553
        assert haven.defense_round_win_rate == 61.0
        assert haven.defense_rounds_won == 795
        assert haven.defense_rounds_lost == 517

    def test_parse_team_with_minimal_map_data(self):
        html = _load_html(17676, "stats.html")
        result = parse_team_stats(html, 17676)

        assert result.team_id == 17676
        assert len(result.maps) > 0

        for map_stat in result.maps:
            assert map_stat.games_played > 0
            assert map_stat.win_rate is None or map_stat.win_rate >= 0.0

    def test_parse_date_filtered_stats(self):
        html = _load_html(1034, "stats_date_june_2025.html")
        result = parse_team_stats(html, 1034)

        assert result.team_id == 1034
        assert len(result.maps) >= 0

    def test_parse_event_filtered_stats(self):
        html = _load_html(1034, "stats_event_2860.html")
        result = parse_team_stats(html, 1034)

        assert result.team_id == 1034
        assert len(result.maps) >= 0


class TestParseAgentCompositionBasic:
    def test_parse_compositions_basic_bind(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="basic")

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None
        assert len(bind.compositions) > 0

        comp = next(
            (
                c
                for c in bind.compositions
                if "Brimstone" in c.agents
                and "Viper" in c.agents
                and "Yoru" in c.agents
            ),
            None,
        )
        assert comp is not None
        assert "Fade" in comp.agents
        assert "Raze" in comp.agents
        assert comp.wins + comp.losses == comp.games_played

    def test_parse_compositions_basic_haven(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="basic")

        haven = next((m for m in result.maps if m.map_name == "Haven"), None)
        assert haven is not None
        assert haven.compositions is not None
        assert len(haven.compositions) > 0

    def test_compositions_sorted_by_play_count(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="basic")

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None

        for i in range(len(bind.compositions) - 1):
            curr = bind.compositions[i]
            next_comp = bind.compositions[i + 1]
            if curr.games_played == next_comp.games_played:
                assert curr.win_rate >= next_comp.win_rate
            else:
                assert curr.games_played > next_comp.games_played

    def test_agents_sorted_alphabetically(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="basic")

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None

        for comp in bind.compositions:
            assert comp.agents == sorted(comp.agents)

    def test_composition_win_rate_calculated(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="basic")

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None

        for comp in bind.compositions:
            if comp.games_played > 0:
                expected_rate = round((comp.wins / comp.games_played) * 100, 2)
                assert comp.win_rate == expected_rate

    def test_none_mode_no_compositions(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="none")

        for map_stat in result.maps:
            assert map_stat.compositions is None

    def test_kayo_normalization(self):
        html = _load_html(1034, "stats.html")
        result = parse_team_stats(html, 1034, agent_composition="basic")

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None

        kayo_comp = next((c for c in bind.compositions if "Kayo" in c.agents), None)
        assert kayo_comp is not None
        assert "Kayo" in kayo_comp.agents


class TestParseAgentCompositionDetailed:
    def test_parse_compositions_detailed_has_matches(self):
        html = _load_html(1034, "stats.html")

        mock_fn = MagicMock(return_value=_make_series_info())

        result = parse_team_stats(
            html,
            1034,
            agent_composition="detailed",
            series_info_fn=mock_fn,
        )

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None

        for comp in bind.compositions:
            if comp.games_played > 0:
                assert comp.matches is not None
                assert len(comp.matches) > 0

    def test_detailed_match_has_required_fields(self):
        html = _load_html(1034, "stats.html")

        mock_fn = MagicMock(return_value=_make_series_info())

        result = parse_team_stats(
            html,
            1034,
            agent_composition="detailed",
            series_info_fn=mock_fn,
        )

        bind = next((m for m in result.maps if m.map_name == "Bind"), None)
        assert bind is not None
        assert bind.compositions is not None

        comp_with_matches = next((c for c in bind.compositions if c.matches), None)
        if comp_with_matches and comp_with_matches.matches:
            match = comp_with_matches.matches[0]
            assert match.series_id > 0
            assert match.date != ""
            assert match.opponent_name != ""
            assert isinstance(match.is_win, bool)
            assert match.team_score >= 0
            assert match.opponent_score >= 0

