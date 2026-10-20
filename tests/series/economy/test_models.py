import vlrdevapi
from tests.conftest import (
    load_fixture,
    mock_vlr,  # noqa: F401
)
from vlrdevapi._series.economy import BuyTierRecord, EconScore

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
        assert round_1.spent_team1 == 4100
        assert round_1.spent_team2 == 4100
        assert round_1.winner.name == "FNC"
        assert round_1.winner.id == 2593
        assert round_1.buy_type_team1 == "Pistol"
        assert round_1.buy_type_team2 == "Pistol"
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
        assert buy_types == {"Pistol", "Eco", "Half-buy", "Full-buy"}

    def test_buy_matrix_summary(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        matrix = result.buy_matrix_team1
        assert matrix.pistol == EconScore(won=2, total=2)
        assert matrix.converted == EconScore(won=2, total=2)
        assert matrix.bonus == EconScore(won=1, total=2)

    def test_buy_matrix_tiers(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        matrix = result.buy_matrix_team1
        assert matrix.on_eco == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=1, total=2),
        )
        assert matrix.on_half_buy == BuyTierRecord(
            vs_eco=None, vs_half=None, vs_full=EconScore(won=1, total=3),
        )
        assert matrix.on_full_buy == BuyTierRecord(
            vs_eco=EconScore(won=1, total=1),
            vs_half=EconScore(won=0, total=1),
            vs_full=EconScore(won=5, total=11),
        )

    def test_winner_side_not_duplicated(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        # Side data lives in series.rounds (RoundData.side), not here.
        assert not hasattr(result.rounds[0], "winner_side")

    def test_winners_distribution(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game={GAME_ID}&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=GAME_ID)
        fnc_wins = [r for r in result.rounds if r.winner.name == "FNC"]
        vit_wins = [r for r in result.rounds if r.winner.name == "VIT"]
        assert len(fnc_wins) == 13
        assert len(vit_wins) == 11

    def test_economy_positional_game_one(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game=1&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=1)
        assert result.series_id == SERIES_ID
        assert result.game_id == 1
        assert result.team1 == "FNC"
        assert result.team1_id == 2593
        assert len(result.rounds) == 24
        assert result.rounds[0].spent_team1 == 4100

    def test_economy_positional_game_two_differs(self, mock_vlr):
        mock_vlr.get(f"/{SERIES_ID}?game=2&tab=economy").respond(200, text=load_fixture("series", "644718", "game_258363_economy.html"))
        mock_vlr.get(f"/{SERIES_ID}").respond(200, text=load_fixture("series", "644718", "overview.html"))
        result = vlrdevapi.series.economy(SERIES_ID, game_id=2)
        assert result.game_id == 2
        assert len(result.rounds) == 23
        assert result.rounds[0].spent_team1 == 3700


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
