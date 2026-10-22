from datetime import date

from selectolax.lexbor import LexborHTMLParser as HTMLParser

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from vlrdevapi._series.info.parser import parse_series_info

_SERIES_FIXTURES = FIXTURES_DIR / "series"


def _load_html(series_dir: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/{series_dir.split('_')[0]}"))
    path = _SERIES_FIXTURES / series_dir / "overview.html"
    if not path.exists():
        raise FileNotFoundError(path)
    return HTMLParser(path.read_text(encoding="utf-8"))


class TestHeadToHead:
    def test_grand_final_head_to_head(self):
        result = parse_series_info(
            _load_html("542272_nrg-vs-fnatic-valorant-champions-2025-gf"),
        )

        assert len(result.head_to_head) == 2

        first = result.head_to_head[0]
        assert first.series_id == 542270
        assert first.url == (
            "https://www.vlr.gg/542270/"
            "fnatic-vs-nrg-valorant-champions-2025-ubf"
        )
        assert first.event_name == "Champions 2025"
        assert first.stage == "UBF"
        assert first.date == date(2025, 10, 3)
        assert first.team1_name == "NRG"
        assert first.team1_score == 2
        assert first.team2_name == "FNATIC"
        assert first.team2_score == 0
        assert first.winner == "team1"

        second = result.head_to_head[1]
        assert second.series_id == 220442
        assert second.team1_score == 0
        assert second.team2_score == 2
        assert second.winner == "team2"

    def test_team_order_follows_the_head_to_head_header(self):
        result = parse_series_info(
            _load_html("754737_loud-vs-team-vitality-valorant-champions-2026-gf"),
        )

        assert len(result.head_to_head) == 2
        first = result.head_to_head[0]
        assert first.series_id == 754736
        assert first.date in (date(2026, 10, 15), date(2026, 10, 16))
        assert first.team1_name == "LOUD"
        assert first.team2_name == "Team Vitality"
        assert (first.team1_score, first.team2_score) == (2, 1)
        assert first.winner == "team1"

    def test_empty_head_to_head(self):
        result = parse_series_info(_load_html("155313"))

        assert result.head_to_head == []
