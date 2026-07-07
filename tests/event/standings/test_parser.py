import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._event.standings.parser import parse_subnav, parse_standings

def _load_event_html(event_id: int, slug: str) -> HTMLParser:
    path = FIXTURES_DIR / "event" / f"{event_id}_{slug}" / "overview.html"
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")

class TestParseStandingsEMEA:
    """VCT 2026: EMEA Stage 1 — Ongoing event with TBD entries."""
    
    def setup_method(self):
        self.html = _load_event_html(2863, "vct-2026-emea-stage-1")
        
    def test_parse_subnav(self):
        stages = parse_subnav(self.html)
        assert len(stages) == 2
        # Order in subnav: Playoffs (May 7-18), Group Stage (Apr 1-May 2)
        assert "/playoffs" in stages[0][0]
        assert stages[0][1] == "Playoffs"
        assert "/group-stage" in stages[1][0]
        assert stages[1][1] == "Group Stage"
        
    def test_parse_standings_entries(self):
        standings = parse_standings(self.html)
        # Overview shows 8 entries (full final standings)
        assert len(standings) == 8
        
        # 1st (Team Heretics)
        assert standings[0].place == "1st"
        assert standings[0].team.name == "Team Heretics"
        assert standings[0].team.id == 1001
        assert standings[0].prize_money is None
        assert standings[0].prize_currency is None
        
        # 3rd (FUT Esports)
        assert standings[2].place == "3rd"
        assert standings[2].team.name == "FUT Esports"

class TestParseStandingsAmericas:
    """VCT 2026: Americas Kickoff — Completed event with points and notes."""
    
    def setup_method(self):
        self.html = _load_event_html(2682, "vct-2026-americas-kickoff")
        
    def test_parse_standings_count(self):
        standings = parse_standings(self.html)
        # 1st to 9th-10th entries are visible in the snippet
        assert len(standings) >= 9

    def test_first_place(self):
        standings = parse_standings(self.html)
        first = standings[0]
        assert first.place == "1st"
        assert first.team.name == "FURIA"
        assert first.team.id == 2406
        assert first.team.country == "Brazil"
        assert first.team.logo_url is not None
        assert "632be843b7d51.png" in first.team.logo_url
        assert first.prize_money is None # Shown as "-" in HTML
        assert first.points == 4
        assert first.note == "Masters Santiago"

    def test_second_place(self):
        standings = parse_standings(self.html)
        second = standings[1]
        assert second.place == "2nd"
        assert second.team.name == "G2 Esports"
        assert second.team.id == 11058
        assert second.team.country == "United States"
        assert second.points == 3
        assert second.note == "Masters Santiago"

    def test_fourth_place(self):
        standings = parse_standings(self.html)
        fourth = standings[3]
        assert fourth.place == "4th"
        assert fourth.team.name == "MIBR"
        assert fourth.points == 1
        assert fourth.note is None

    def test_seventh_eighth_place(self):
        standings = parse_standings(self.html)
        # 7th-8th entries are at index 6 and 7
        eg = standings[6]
        lev = standings[7]
        assert eg.place == "7th–8th"
        assert eg.team.name == "Evil Geniuses"
        assert lev.place == "7th–8th"
        assert lev.team.name == "LEVIATÁN"

class TestParseStandingsJapan:
    """Challengers 2026: Japan Split 1 — Prize money in JPY."""
    
    def setup_method(self):
        self.html = _load_event_html(2847, "challengers-2026-japan-split-1")
        
    def test_parse_standings_count(self):
        standings = parse_standings(self.html)
        assert len(standings) == 4

    def test_first_place(self):
        standings = parse_standings(self.html)
        first = standings[0]
        assert first.place == "1st"
        assert first.team.name == "CREST GAMING Zst"
        assert first.team.id == 294
        # Prize: ¥1,500,000
        assert first.prize_money == 1500000
        assert first.prize_currency == "¥"
        assert first.note == "Split 2"

    def test_third_fourth_place(self):
        standings = parse_standings(self.html)
        # 3rd-4th are at index 2 and 3
        entry = standings[2]
        assert entry.place == "3rd–4th"
        assert entry.team.name == "Insomnia"
        assert entry.prize_money == 500000
        assert entry.prize_currency == "¥"
        assert entry.note == "Split 2"

