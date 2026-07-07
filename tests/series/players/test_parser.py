import pytest

from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._series.players.parser import parse_players_stats


_FIXTURES = (
    FIXTURES_DIR
    / "series"
    / "542272_nrg-vs-fnatic-valorant-champions-2025-gf"
)


def _load_html(filename: str) -> HTMLParser:
    path = _FIXTURES / filename
    return HTMLParser(path.read_text(encoding="utf-8"))



class TestParseGameAll:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_players_stats(_load_html("overview.html"), game_id="all")

    def test_team1_info(self):
        assert self.result.team1.team_id == 1034
        assert self.result.team1.team_name == "NRG"
        assert self.result.team1.team_short == "NRG"

    def test_team2_info(self):
        assert self.result.team2.team_id == 2593
        assert self.result.team2.team_name == "FNATIC"
        assert self.result.team2.team_short == "FNC"

    def test_team1_player_count(self):
        assert len(self.result.team1.players) == 5

    def test_team2_player_count(self):
        assert len(self.result.team2.players) == 5

    def test_brawk_all_stats(self):
        brawk = self.result.team1.players[0]
        assert brawk.player_id == 2172
        assert brawk.name == "brawk"
        assert brawk.country_code == "us"
        assert brawk.country == "United States"
        assert brawk.team_short == "NRG"
        assert brawk.agents == ["Sova", "Vyse"]

        assert brawk.stats.overall.rating == 1.27
        assert brawk.stats.overall.acs == 244.0
        assert brawk.stats.overall.kills == 84
        assert brawk.stats.overall.deaths == 61
        assert brawk.stats.overall.assists == 40
        assert brawk.stats.overall.kd_diff == 23
        assert brawk.stats.overall.kast == pytest.approx(0.81, abs=0.01)
        assert brawk.stats.overall.adr == 151.0
        assert brawk.stats.overall.hs_percent == pytest.approx(0.21, abs=0.01)
        assert brawk.stats.overall.first_kills == 7
        assert brawk.stats.overall.first_deaths == 5
        assert brawk.stats.overall.fk_fd_diff == 2

        assert brawk.stats.attack.rating == 1.24
        assert brawk.stats.attack.acs == 237.0
        assert brawk.stats.attack.kills == 40
        assert brawk.stats.attack.deaths == 32
        assert brawk.stats.attack.assists == 20
        assert brawk.stats.attack.kd_diff == 8
        assert brawk.stats.attack.kast == pytest.approx(0.75, abs=0.01)
        assert brawk.stats.attack.adr == 152.0
        assert brawk.stats.attack.hs_percent == pytest.approx(0.21, abs=0.01)
        assert brawk.stats.attack.first_kills == 2
        assert brawk.stats.attack.first_deaths == 3
        assert brawk.stats.attack.fk_fd_diff == -1

        assert brawk.stats.defend.rating == 1.30
        assert brawk.stats.defend.acs == 241.0
        assert brawk.stats.defend.kills == 44
        assert brawk.stats.defend.deaths == 29
        assert brawk.stats.defend.assists == 20
        assert brawk.stats.defend.kd_diff == 15
        assert brawk.stats.defend.kast == pytest.approx(0.88, abs=0.01)
        assert brawk.stats.defend.adr == 150.0
        assert brawk.stats.defend.hs_percent == pytest.approx(0.21, abs=0.01)
        assert brawk.stats.defend.first_kills == 5
        assert brawk.stats.defend.first_deaths == 2
        assert brawk.stats.defend.fk_fd_diff == 3

    def test_map_name_empty_for_all(self):
        assert self.result.map_name == ""

    def test_game_id_is_all(self):
        assert self.result.game_id == "all"


class TestParseGame233478:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.result = parse_players_stats(
            _load_html("game_233478_overview.html"), game_id="233478"
        )

    def test_map_name(self):
        assert self.result.map_name == "Corrode"

    def test_team1_info(self):
        assert self.result.team1.team_id == 1034
        assert self.result.team1.team_name == "NRG"

    def test_team2_info(self):
        assert self.result.team2.team_id == 2593
        assert self.result.team2.team_name == "FNATIC"

    def test_team1_player_count(self):
        assert len(self.result.team1.players) == 5

    def test_team2_player_count(self):
        assert len(self.result.team2.players) == 5

    def test_brawk_game_stats(self):
        brawk = self.result.team1.players[0]
        assert brawk.player_id == 2172
        assert brawk.name == "brawk"
        assert brawk.country_code == "us"
        assert brawk.country == "United States"
        assert brawk.agents == ["Sova"]

        assert brawk.stats.overall.rating == 1.93
        assert brawk.stats.overall.acs == 375.0
        assert brawk.stats.overall.kills == 24
        assert brawk.stats.overall.deaths == 7
        assert brawk.stats.overall.assists == 2
        assert brawk.stats.overall.kd_diff == 17
        assert brawk.stats.overall.kast == pytest.approx(0.94, abs=0.01)
        assert brawk.stats.overall.adr == 212.0
        assert brawk.stats.overall.hs_percent == pytest.approx(0.19, abs=0.01)
        assert brawk.stats.overall.first_kills == 1
        assert brawk.stats.overall.first_deaths == 1
        assert brawk.stats.overall.fk_fd_diff == 0

        assert brawk.stats.attack.rating == 2.13
        assert brawk.stats.attack.acs == 410.0
        assert brawk.stats.attack.kills == 7
        assert brawk.stats.attack.deaths == 1
        assert brawk.stats.attack.assists == 0
        assert brawk.stats.attack.kd_diff == 6
        assert brawk.stats.attack.kast == pytest.approx(0.75, abs=0.01)
        assert brawk.stats.attack.adr == 230.0
        assert brawk.stats.attack.hs_percent == pytest.approx(0.16, abs=0.01)
        assert brawk.stats.attack.first_kills == 0
        assert brawk.stats.attack.first_deaths == 0
        assert brawk.stats.attack.fk_fd_diff == 0

        assert brawk.stats.defend.rating == 1.87
        assert brawk.stats.defend.acs == 364.0
        assert brawk.stats.defend.kills == 17
        assert brawk.stats.defend.deaths == 6
        assert brawk.stats.defend.assists == 2
        assert brawk.stats.defend.kd_diff == 11
        assert brawk.stats.defend.kast == pytest.approx(1.0, abs=0.01)
        assert brawk.stats.defend.adr == 206.0
        assert brawk.stats.defend.hs_percent == pytest.approx(0.20, abs=0.01)
        assert brawk.stats.defend.first_kills == 1
        assert brawk.stats.defend.first_deaths == 1
        assert brawk.stats.defend.fk_fd_diff == 0

    def test_mada_game_stats(self):
        mada = self.result.team1.players[1]
        assert mada.player_id == 5132
        assert mada.name == "mada"
        assert mada.country_code == "ca"
        assert mada.country == "Canada"
        assert mada.stats.overall.rating == 1.41
        assert mada.stats.overall.acs == 295.0

