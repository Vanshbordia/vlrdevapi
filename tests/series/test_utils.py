from pathlib import Path

import pytest
from selectolax.parser import HTMLParser

from vlrdevapi._series._utils import _extract_team_abbreviations

_FIXTURES = Path(__file__).resolve().parent.parent / "test_html" / "series"


def _load_overview(series_dir: str) -> HTMLParser:
    path = _FIXTURES / series_dir / "overview.html"
    if not path.exists():
        pytest.fail(f"Fixture not found: {path}")
    return HTMLParser(path.read_text(encoding="utf-8"))


class TestExtractTeamAbbreviations:
    def test_704037_mushoku_vs_fallen_angels(self):
        html = _load_overview("704037")
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == "Mush"
        assert t2 == "Fall"

    def test_64819_madness_vs_huat_zai(self):
        html = _load_overview("64819")
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == "MAD"
        assert t2 == "HZ"

    def test_30788_cynical_vs_nxlg_academy(self):
        html = _load_overview("30788")
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == "CNL"
        assert t2 == "NXLGA"

    def test_542272_nrg_vs_fnatic(self):
        html = _load_overview("542272_nrg-vs-fnatic-valorant-champions-2025-gf")
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == "NRG"
        assert t2 == "FNC"

    def test_644718_fnatic_vs_vitality(self):
        html = _load_overview("644718")
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == "FNC"
        assert t2 == "VIT"

    def test_empty_when_no_ovw_tables(self):
        html = HTMLParser("<html><body><p>nothing</p></body></html>")
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == ""
        assert t2 == ""

    def test_empty_when_single_table(self):
        html = HTMLParser(
            '<html><body><div class="ovw-table">'
            '<div class="ovw-player-tag">ABC</div>'
            "</div></body></html>"
        )
        t1, t2 = _extract_team_abbreviations(html)
        assert t1 == ""
        assert t2 == ""
