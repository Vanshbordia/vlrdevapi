from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from vlrdevapi._series._utils import resolve_game_id

_FIXTURE = HTMLParser(
    load_fixture(
        "series",
        "542272_nrg-vs-fnatic-valorant-champions-2025-gf",
        "overview.html",
    ),
)


class TestResolveGameId:
    def test_all(self):
        assert resolve_game_id(_FIXTURE, "all") == "all"

    def test_all_case_insensitive(self):
        assert resolve_game_id(_FIXTURE, "ALL") == "all"

    def test_positional_first(self):
        assert resolve_game_id(_FIXTURE, 1) == "233478"
        assert resolve_game_id(_FIXTURE, "1") == "233478"

    def test_positional_last(self):
        assert resolve_game_id(_FIXTURE, 5) == "233482"

    def test_real_id_passthrough(self):
        assert resolve_game_id(_FIXTURE, 233479) == "233479"
        assert resolve_game_id(_FIXTURE, "233479") == "233479"

    def test_out_of_range_returns_input(self):
        assert resolve_game_id(_FIXTURE, 99) == "99"

    def test_non_numeric_passthrough(self):
        assert resolve_game_id(_FIXTURE, "abc") == "abc"
