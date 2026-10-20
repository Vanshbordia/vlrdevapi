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

    def test_rounds_positional_game_one(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game=1&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=1)
        assert result.series_id == SERIES_ID
        assert result.game_id == 1
        assert len(result.rounds) == 24
        assert result.rounds[0].round_number == 1

    def test_rounds_positional_game_two_differs(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game=2&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=2)
        assert result.game_id == 2
        assert len(result.rounds) == 23


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


_GF_2022 = "130685_loud-vs-optic-gaming-valorant-champions-2022-gf"


class TestRoundsEconomyEnrichment:
    """The rounds namespace merges bank/spend/buy types from the economy tab."""

    def test_first_round_details(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=GAME_ID)
        round_1 = result.rounds[0]
        assert round_1.bank_team1 == 100.0
        assert round_1.bank_team2 == 100.0
        assert round_1.spent_team1 == 4100
        assert round_1.spent_team2 == 4100
        assert round_1.buy_type_team1 == "Pistol"
        assert round_1.buy_type_team2 == "Pistol"
        assert round_1.is_pistol_round is True

    def test_130685_ascent_rounds_merge(self, mock_vlr):
        mock_vlr.get("/130685?game=95131&tab=overview").respond(200, text=load_fixture("series", _GF_2022, "game_95131_overview.html"))
        mock_vlr.get("/130685?game=95131&tab=economy").respond(200, text=load_fixture("series", _GF_2022, "game_95131_economy.html"))
        mock_vlr.get("/130685").respond(200, text=load_fixture("series", _GF_2022, "overview.html"))
        result = vlrdevapi.series.rounds(130685, game_id=95131)
        assert result.team1 == "LOUD"
        r1, r2 = result.rounds[0], result.rounds[1]
        assert (r1.bank_team1, r1.bank_team2) == (400.0, 100.0)
        assert (r1.spent_team1, r1.spent_team2) == (3800, 3700)
        assert r1.buy_type_team1 == "Pistol"
        assert r1.buy_type_team2 == "Pistol"
        assert r1.is_pistol_round is True
        assert r1.side == "Attack"
        assert r2.buy_type_team1 == "Full-buy"
        assert r2.buy_type_team2 == "Eco"
        assert r2.is_pistol_round is False

    def test_graceful_without_economy_page(self, mock_vlr):
        # No economy route mocked: rounds still work, economy fields stay None.
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=overview").respond(200, text=load_fixture("series", "644718", "game_258363_rounds.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.rounds(SERIES_ID, game_id=GAME_ID)
        assert len(result.rounds) == 24
        for r in result.rounds:
            assert r.bank_team1 is None
            assert r.buy_type_team1 == ""
            assert r.spent_team1 is None
