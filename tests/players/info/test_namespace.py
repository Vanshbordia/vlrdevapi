from tests.conftest import load_fixture
import vlrdevapi


class TestSyncModuleLevel:
    def test_ethan_info(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        result = vlrdevapi.player.info(11225)
        assert result.player_id == 11225
        assert result.name == "Ethan"
        assert result.real_name == "Ethan Arnold"
        assert result.country_code == "us"
        assert result.x_link == "https://x.com/ethanarnold"
        assert result.x_handle == "@ethanarnold"
        assert result.twitch_link == "https://www.twitch.tv/ethancs"
        assert result.twitch_handle == "ethancs"
        assert result.aliases == []

    def test_inspire_info(self, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))

        result = vlrdevapi.player.info(53)
        assert result.player_id == 53
        assert result.name == "Inspire"
        assert result.real_name == "Hunter Schline"
        assert result.country_code == "us"
        assert result.x_link == "https://x.com/Inspire_Val"
        assert result.x_handle == "@Inspire_Val"
        assert result.twitch_link == "https://www.twitch.tv/inspire"
        assert result.twitch_handle == "inspire"
        assert result.aliases == ["BxbyJ", "BabyJ"]


class TestSyncWithClient:
    def test_ethan_info(self, mock_vlr):
        mock_vlr.get("/player/11225").respond(200, text=load_fixture("player", "11225_ethan", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.info(11225)
        assert result.player_id == 11225
        assert result.name == "Ethan"
        assert result.real_name == "Ethan Arnold"
        assert result.country_code == "us"

    def test_inspire_info(self, mock_vlr):
        mock_vlr.get("/player/53").respond(200, text=load_fixture("player", "53_inspire", "overview.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.player.info(53)
        assert result.player_id == 53
        assert result.name == "Inspire"
        assert result.aliases == ["BxbyJ", "BabyJ"]

