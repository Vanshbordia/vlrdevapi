from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi

SERIES_ID = 644718
GAME_ID = 258363


class TestSyncModuleLevel:
    def test_rounds_specific_game(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=GAME_ID)
        assert result.series_id == SERIES_ID
        assert result.game_id == GAME_ID
        assert result.team1 == "FNC"
        assert result.team1_id == 2593
        assert result.team2 == "VIT"
        assert result.team2_id == 2059
        assert len(result.rounds) == 24

    def test_first_round_details(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=GAME_ID)
        round_1 = result.rounds[0]
        assert round_1.round_number == 1
        assert round_1.winner_team_name == "FNC"
        assert round_1.winner_team_id == 2593
        assert round_1.win_type == "Time out"
        assert round_1.side == "Defense"
        assert round_1.team1_score == 1
        assert round_1.team2_score == 0

    def test_rounds_have_correct_winners(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=GAME_ID)
        fnc_wins = [r for r in result.rounds if r.winner_team_name == "FNC"]
        vit_wins = [r for r in result.rounds if r.winner_team_name == "VIT"]
        assert len(fnc_wins) == 13
        assert len(vit_wins) == 11

    def test_win_types_present(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=GAME_ID)
        win_types = set(r.win_type for r in result.rounds)
        assert win_types == {"Elimination", "Defuse", "Spike detonation", "Time out"}


class TestSyncWithClient:
    def test_rounds_specific_game(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        with vlrdevapi.VLRClient() as client:
            result = client.series.rounds(SERIES_ID, game_id=GAME_ID)
        assert result.series_id == SERIES_ID
        assert result.team1_id == 2593
        assert result.team2_id == 2059

    def test_curried_match_rounds(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        with vlrdevapi.VLRClient() as client:
            match = client.series(SERIES_ID)
            result = match.rounds(game_id=GAME_ID)
        assert result.series_id == SERIES_ID
        assert len(result.rounds) == 24
