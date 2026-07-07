import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._player.info.parser import parse_player_info

_FIXTURES = FIXTURES_DIR / "player"

def _load_html(player_dir: str, filename: str) -> HTMLParser:
    path = _FIXTURES / player_dir / filename
    return HTMLParser(path.read_text(encoding="utf-8"))

class TestParseEthan:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_player_info(_load_html("11225_ethan", "overview.html"))
        self.result.player_id = 11225

    def test_name(self):
        assert self.result.name == "Ethan"

    def test_real_name(self):
        assert self.result.real_name == "Ethan Arnold"

    def test_img(self):
        assert self.result.img.startswith("https://owcdn.net/")

    def test_x_link(self):
        assert self.result.x_link == "https://x.com/ethanarnold"

    def test_x_handle(self):
        assert self.result.x_handle == "@ethanarnold"

    def test_twitch_link(self):
        assert self.result.twitch_link == "https://www.twitch.tv/ethancs"

    def test_twitch_handle(self):
        assert self.result.twitch_handle == "ethancs"

    def test_country(self):
        assert self.result.country == "United States"

    def test_country_code(self):
        assert self.result.country_code == "us"

    def test_aliases_empty(self):
        assert self.result.aliases == []

    def test_player_id(self):
        assert self.result.player_id == 11225

class TestParseInspire:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_player_info(_load_html("53_inspire", "overview.html"))
        self.result.player_id = 53

    def test_name(self):
        assert self.result.name == "Inspire"

    def test_real_name(self):
        assert self.result.real_name == "Hunter Schline"

    def test_img(self):
        assert self.result.img.startswith("https://owcdn.net/")

    def test_x_link(self):
        assert self.result.x_link == "https://x.com/Inspire_Val"

    def test_x_handle(self):
        assert self.result.x_handle == "@Inspire_Val"

    def test_twitch_link(self):
        assert self.result.twitch_link == "https://www.twitch.tv/inspire"

    def test_twitch_handle(self):
        assert self.result.twitch_handle == "inspire"

    def test_country(self):
        assert self.result.country == "United States"

    def test_country_code(self):
        assert self.result.country_code == "us"

    def test_aliases(self):
        assert self.result.aliases == ["BxbyJ", "BabyJ"]

    def test_player_id(self):
        assert self.result.player_id == 53

