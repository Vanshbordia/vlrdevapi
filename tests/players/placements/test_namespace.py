from tests.conftest import load_fixture
import vlrdevapi


class TestSyncModuleLevel:
    def test_yuvi_placements(self, mock_vlr):
        mock_vlr.get("/player/46051").respond(
            200, text=load_fixture("player", "46051_yuvi", "overview.html"),
        )

        result = vlrdevapi.player.placements(46051)
        assert result.player_id == 46051
        assert result.total_winnings == 5082
        assert result.total_winnings_currency == "$"
        assert len(result.placements) == 13
        assert result.placements[0].event_name == (
            "Challengers 2026: South Asia Split 2"
        )

    def test_curried_placements(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(
            200, text=load_fixture("player", "11225_ethan", "overview.html"),
        )

        result = vlrdevapi.player(11225).placements()
        assert result.player_id == 11225
        assert result.total_winnings == 645700
        assert len(result.placements) == 45


class TestSyncWithClient:
    def test_inspire_placements(self, mock_vlr):
        mock_vlr.get("/player/53").respond(
            200, text=load_fixture("player", "53_inspire", "overview.html"),
        )

        with vlrdevapi.VLRClient() as client:
            result = client.player.placements(53)
        assert result.player_id == 53
        assert result.total_winnings == 28450
        assert len(result.placements) == 27
