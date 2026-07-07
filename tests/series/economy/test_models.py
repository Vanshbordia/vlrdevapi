from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi

SERIES_ID = 644718
GAME_ID = 258363


class TestSyncModuleLevel:
    def test_economy_specific_game(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        assert result.series_id == SERIES_ID
        assert result.game_id == GAME_ID
        assert result.team1 == "FNC"
        assert result.team1_id == 2593
        assert result.team2 == "VIT"
        assert result.team2_id == 2059
        assert len(result.rounds) == 24

    def test_first_round_details(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        round_1 = result.rounds[0]
        assert round_1.round_number == 1
        assert round_1.bank_team1 == 100.0
        assert round_1.bank_team2 == 100.0
        assert round_1.spent_team1 == 4050
        assert round_1.spent_team2 == 4100
        assert round_1.winner.name == "FNC"
        assert round_1.winner.id == 2593
        assert round_1.buy_type_team1 == "Eco"
        assert round_1.buy_type_team2 == "Eco"
        assert round_1.is_pistol_round is True

    def test_pistol_rounds(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        pistol_rounds = [r for r in result.rounds if r.is_pistol_round]
        assert len(pistol_rounds) == 2
        assert pistol_rounds[0].round_number == 1
        assert pistol_rounds[1].round_number == 13

    def test_buy_types_variety(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        buy_types = set()
        for round_data in result.rounds:
            buy_types.add(round_data.buy_type_team1)
            buy_types.add(round_data.buy_type_team2)
        assert buy_types == {"Eco", "Semi-eco", "Semi-buy", "Full-buy"}

    def test_winners_distribution(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        fnc_wins = [r for r in result.rounds if r.winner.name == "FNC"]
        vit_wins = [r for r in result.rounds if r.winner.name == "VIT"]
        assert len(fnc_wins) == 13
        assert len(vit_wins) == 11


class TestSyncWithClient:
    def test_economy_specific_game(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        with vlrdevapi.VLRClient() as client:
            result = client.series.economy(SERIES_ID, game_id=GAME_ID)
        assert result.series_id == SERIES_ID
        assert result.team1_id == 2593
        assert result.team2_id == 2059

    def test_curried_match_economy(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        with vlrdevapi.VLRClient() as client:
            match = client.series(SERIES_ID)
            result = match.economy(game_id=GAME_ID)
        assert result.series_id == SERIES_ID
        assert len(result.rounds) == 24
