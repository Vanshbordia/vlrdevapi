import pytest

import vlrdevapi
from tests.conftest import load_fixture, mock_vlr  # noqa: F401
from vlrdevapi._series.players.models import PlayerGameStats, PlayersStats, TeamPlayers
from vlrdevapi._series.replay.models import ReplayEventType
from vlrdevapi._series.replay.namespace import _apply_id_resolution, _attach_player_ids

DIR_283288 = "754737_loud-vs-team-vitality-valorant-champions-2026-gf"
SERIES_ID = 754737
GAME_ID = 283288


def _mock_logs(mock_vlr, series_id=SERIES_ID, game_id=GAME_ID):
    mock_vlr.get(f"/{series_id}?game={game_id}&tab=logs").respond(
        200,
        text=load_fixture("series", DIR_283288, f"game_{game_id}_logs.html"),
    )


def _mock_overview(mock_vlr, series_id=SERIES_ID, game_id=GAME_ID):
    mock_vlr.get(f"/{series_id}?game={game_id}&tab=overview").respond(
        200,
        text=load_fixture("series", DIR_283288, f"game_{game_id}_overview.html"),
    )


def _stats(*, dup_names: bool = False) -> PlayersStats:
    """Hand-assigned overview stats for the 2026 GF game's rosters.

    With ``dup_names``, both teams get a player named ``ace`` with
    different IDs - the adversarial case matcher must survive.

    """
    t1 = [
        PlayerGameStats(player_id=41224, name="tkzin", team_short="LOD"),
        PlayerGameStats(player_id=29242, name="erde", team_short="LOD"),
        PlayerGameStats(player_id=10885, name="DaviH", team_short="LOD"),
    ]
    t2 = [
        PlayerGameStats(player_id=458, name="Chronicle", team_short="VIT"),
        PlayerGameStats(player_id=9780, name="Jamppi", team_short="VIT"),
        PlayerGameStats(player_id=5022, name="Derke", team_short="VIT"),
    ]
    if dup_names:
        t1.append(PlayerGameStats(player_id=111, name="ace", team_short="LOD"))
        t2.append(PlayerGameStats(player_id=222, name="ace", team_short="VIT"))
    return PlayersStats(
        team1=TeamPlayers(team_id=6961, team_name="LOUD", team_short="LOD", players=t1),
        team2=TeamPlayers(team_id=2059, team_name="Team Vitality", team_short="VIT", players=t2),
    )


def _replay():
    """Parse the real 283288 logs fixture for enrichment tests."""
    from selectolax.lexbor import LexborHTMLParser

    from vlrdevapi._series.replay.parser import parse_replay_data

    html = LexborHTMLParser(load_fixture("series", DIR_283288, "game_283288_logs.html"))
    return parse_replay_data(html, game_id=GAME_ID)


class TestEnrichment:
    def test_team_ids_and_player_ids(self, mock_vlr):
        _mock_logs(mock_vlr)
        _mock_overview(mock_vlr)
        result = vlrdevapi.series.replay(SERIES_ID, game_id=GAME_ID)
        assert result.team1_id == 6961  # LOUD
        assert result.team2_id == 2059  # Team Vitality
        players = result.round(1).players
        assert {p.name: p.player_id for p in players} == {
            "erde": 29242,
            "tkzin": 41224,
            "Darker": 10557,
            "DaviH": 10885,
            "lukxo": 28716,
            "Chronicle": 458,
            "Sayonara": 33902,
            "PROFEK": 5554,
            "Derke": 5022,
            "Jamppi": 9780,
        }

    def test_actor_victim_alive_ids(self, mock_vlr):
        _mock_logs(mock_vlr)
        _mock_overview(mock_vlr)
        result = vlrdevapi.series.replay(SERIES_ID, game_id=GAME_ID)
        first_kill = result.round(1).events[0]
        assert first_kill.actor.name == "tkzin"
        assert first_kill.actor.player_id == 41224
        assert first_kill.victim.name == "Jamppi"
        assert first_kill.victim.player_id == 9780
        assert {p.name: p.player_id for p in first_kill.alive}["Derke"] == 5022
        # Derived events get IDs too, via the revived player.
        resurrect = [
            e for rd in result.rounds for e in rd.events
            if e.type is ReplayEventType.RESURRECT
        ]
        assert {e.actor.name: e.actor.player_id for e in resurrect} == {
            "DaviH": 10885,
            "tkzin": 41224,
        }

    def test_curried_access(self, mock_vlr):
        _mock_logs(mock_vlr)
        _mock_overview(mock_vlr)
        with vlrdevapi.VLRClient() as client:
            result = client.series(SERIES_ID).replay(GAME_ID)
        assert result.series_id == SERIES_ID
        assert result.team1_id == 6961
        assert len(result.round(9).events) == 9

    def test_unplayed_map_skips_overview(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game=283290&tab=logs").respond(
            200,
            text=load_fixture("series", DIR_283288, "game_283290_logs.html"),
        )
        result = vlrdevapi.series.replay(SERIES_ID, game_id=283290)
        assert result.rounds == []
        assert result.num_rounds == 0
        assert result.team1_id == 0  # no enrichment on an unplayed map

    def test_played_map_without_stat_tables_degrades(self, mock_vlr):
        # Overview tab reachable but carrying no stat tables (VLR hiccup):
        # header team IDs still land, player IDs degrade to 0.
        _mock_logs(mock_vlr)
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(
            200,
            text=load_fixture("series", DIR_283288, "game_283288_logs.html"),
        )
        result = vlrdevapi.series.replay(SERIES_ID, game_id=GAME_ID)
        assert result.team1_id == 6961  # still via the raw match header links
        assert result.team2_id == 2059
        assert result.num_rounds == 18
        first_kill = result.round(1).events[0]
        assert first_kill.actor.name == "tkzin"
        assert first_kill.actor.player_id == 0

    def test_overview_fetch_failure_degrades(self, mock_vlr):
        _mock_logs(mock_vlr)
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(500)
        result = vlrdevapi.series.replay(SERIES_ID, game_id=GAME_ID)
        # Timeline still comes back; IDs simply stay unresolved.
        assert result.num_rounds == 18
        assert result.team1 == "LOUD"
        assert result.team1_id == 0


@pytest.mark.parametrize(
    ("team", "name", "expected"),
    [
        ("LOUD", "tkzin", 41224),  # team-keyed exact match
        ("Team Vitality", "Jamppi", 9780),
        ("LOUD", "DaviH", 10885),
        ("", "Derke", 5022),  # team-less: unique-name fallback
        ("Team Vitality", "Derke", 5022),
        ("LOUD", "nobody here", 0),  # unknown name keeps 0
    ],
)
def test_resolver(team, name, expected):
    """The core matcher: team-scoped by name, never agent, no cross-team leak."""
    result = _replay()
    alive = result.round(9).events[0].alive
    probe = alive[0]
    probe.team = team
    probe.name = name
    _apply_id_resolution(result, _stats())
    assert probe.player_id == expected


def test_duplicate_ign_never_resolves_to_other_team():
    """Same IGN on both teams: no team context -> 0, never a stolen ID."""
    result = _replay()
    _apply_id_resolution(result, _stats(dup_names=True))
    players = result.round(1).players
    ids = {p.name: p.player_id for p in players}
    assert ids["tkzin"] == 41224
    assert ids["Jamppi"] == 9780
    first_kill = result.round(1).events[0]
    assert first_kill.actor.name == "tkzin"
    assert first_kill.actor.player_id == 41224
    assert first_kill.victim.name == "Jamppi"
    assert first_kill.victim.player_id == 9780


def test_team_ids_matched_from_stat_header():
    result = _replay()
    _apply_id_resolution(result, _stats())
    assert result.team1_id == 6961
    assert result.team2_id == 2059


def test_attach_player_ids_from_fixtures():
    """End-to-end enrichment path against the real fixture pair."""
    from selectolax.lexbor import LexborHTMLParser

    result = _replay()
    html = LexborHTMLParser(
        load_fixture("series", DIR_283288, "game_283288_overview.html"),
    )
    _attach_player_ids(result, html, GAME_ID)
    assert result.team1_id == 6961
    assert {p.name: p.player_id for p in result.round(1).players}["Chronicle"] == 458
