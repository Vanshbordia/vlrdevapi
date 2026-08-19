"""Enrichment tests: verify team1_id/team2_id are populated correctly.

Each test loads a series overview + game-specific page, calls the
full namespace function (via mock_vlr), and asserts that team IDs
were resolved from the header links rather than left at zero.
"""

from tests.conftest import load_fixture, mock_vlr  # noqa: F401
import vlrdevapi


class TestEconomyEnrichment704037:
    """Bo1, no veto — economy page uses full team names."""

    SERIES_ID = 704037
    GAME_ID = 274641
    OVW = "series/704037/overview.html"
    ECON = "series/704037/game_274641_economy.html"

    def test_team_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        assert result.team1 == "Mushoku"
        assert result.team1_id == 22117
        assert result.team2 == "Fallen Angels"
        assert result.team2_id == 22762

    def test_winner_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        for rd in result.rounds:
            assert rd.winner.id in (22117, 22762), (
                f"Round {rd.round_number}: winner.id={rd.winner.id}"
            )


class TestEconomyEnrichment64819:
    """Bo1, bans+decider veto — economy page uses abbreviations."""

    SERIES_ID = 64819
    GAME_ID = 65212
    OVW = "series/64819/overview.html"
    ECON = "series/64819/game_65212_economy.html"

    def test_team_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        assert result.team1 == "MAD"
        assert result.team1_id == 7980
        assert result.team2 == "HZ"
        assert result.team2_id == 6718

    def test_winner_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        for rd in result.rounds:
            assert rd.winner.id in (7980, 6718), (
                f"Round {rd.round_number}: winner.id={rd.winner.id}"
            )


class TestEconomyEnrichment30788:
    """Bo1, pick veto — economy page uses abbreviations."""

    SERIES_ID = 30788
    GAME_ID = 47971
    OVW = "series/30788/overview.html"
    ECON = "series/30788/game_47971_economy.html"

    def test_team_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        assert result.team1 == "CNL"
        assert result.team1_id == 4893
        assert result.team2 == "NXLGA"
        assert result.team2_id == 5541

    def test_winner_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        for rd in result.rounds:
            assert rd.winner.id in (4893, 5541), (
                f"Round {rd.round_number}: winner.id={rd.winner.id}"
            )


class TestEconomyEnrichment542272:
    """Bo5 grand final — economy page uses abbreviations."""

    SERIES_ID = 542272
    GAME_ID = 233478
    OVW = "series/542272_nrg-vs-fnatic-valorant-champions-2025-gf/overview.html"
    ECON = "series/542272_nrg-vs-fnatic-valorant-champions-2025-gf/game_233478_economy.html"

    def test_team_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        assert result.team1 == "NRG"
        assert result.team1_id == 1034
        assert result.team2 == "FNC"
        assert result.team2_id == 2593

    def test_winner_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=economy").respond(
            200, text=load_fixture(self.ECON)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.economy(self.SERIES_ID, game_id=self.GAME_ID)
        for rd in result.rounds:
            assert rd.winner.id in (1034, 2593), (
                f"Round {rd.round_number}: winner.id={rd.winner.id}"
            )


class TestRoundsEnrichment644718:
    """Bo3 — rounds page uses abbreviations."""

    SERIES_ID = 644718
    GAME_ID = 258363
    OVW = "series/644718/overview.html"
    ROUNDS = "series/644718/game_258363_rounds.html"

    def test_team_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=overview").respond(
            200, text=load_fixture(self.ROUNDS)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.rounds(self.SERIES_ID, game_id=self.GAME_ID)
        assert result.team1 == "FNC"
        assert result.team1_id == 2593
        assert result.team2 == "VIT"
        assert result.team2_id == 2059

    def test_winner_ids(self, mock_vlr):
        mock_vlr.get(f"/{self.SERIES_ID}?game={self.GAME_ID}&tab=overview").respond(
            200, text=load_fixture(self.ROUNDS)
        )
        mock_vlr.get(f"/{self.SERIES_ID}").respond(200, text=load_fixture(self.OVW))
        result = vlrdevapi.series.rounds(self.SERIES_ID, game_id=self.GAME_ID)
        for rd in result.rounds:
            assert rd.winner_team_id in (2593, 2059), (
                f"Round {rd.round_number}: winner_team_id={rd.winner_team_id}"
            )
