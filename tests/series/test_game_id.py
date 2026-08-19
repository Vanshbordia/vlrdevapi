import pytest
from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from vlrdevapi._series._utils import resolve_game_id
from vlrdevapi.exceptions import ParsingError

_MULTI_MAP = HTMLParser(
    load_fixture(
        "series",
        "542272_nrg-vs-fnatic-valorant-champions-2025-gf",
        "overview.html",
    ),
)

_BO1 = HTMLParser(
    load_fixture(
        "series",
        "704037",
        "overview.html",
    ),
)


class TestResolveGameId:
    def test_all(self):
        assert resolve_game_id(_MULTI_MAP, "all") == "all"

    def test_all_case_insensitive(self):
        assert resolve_game_id(_MULTI_MAP, "ALL") == "all"

    def test_positional_first(self):
        assert resolve_game_id(_MULTI_MAP, 1) == "233478"
        assert resolve_game_id(_MULTI_MAP, "1") == "233478"

    def test_positional_last(self):
        assert resolve_game_id(_MULTI_MAP, 5) == "233482"

    def test_real_id_passthrough(self):
        assert resolve_game_id(_MULTI_MAP, 233479) == "233479"
        assert resolve_game_id(_MULTI_MAP, "233479") == "233479"

    def test_out_of_range_raises(self):
        with pytest.raises(ParsingError, match="index out of range"):
            resolve_game_id(_MULTI_MAP, 99)

    def test_non_numeric_passthrough(self):
        assert resolve_game_id(_MULTI_MAP, "abc") == "abc"


class TestResolveGameIdBo1:
    def test_all(self):
        assert resolve_game_id(_BO1, "all") == "all"

    def test_positional_single_game(self):
        assert resolve_game_id(_BO1, 1) == "274641"

    def test_positional_string(self):
        assert resolve_game_id(_BO1, "1") == "274641"

    def test_real_id_passthrough(self):
        assert resolve_game_id(_BO1, 274641) == "274641"

    def test_out_of_range_raises(self):
        with pytest.raises(ParsingError, match="index out of range"):
            resolve_game_id(_BO1, 2)

    def test_no_games_raises(self):
        html = HTMLParser("<html><body></body></html>")
        with pytest.raises(ParsingError, match="no games found"):
            resolve_game_id(html, 1)

    def test_non_numeric_passthrough(self):
        assert resolve_game_id(_BO1, "abc") == "abc"
