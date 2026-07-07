import pytest
from selectolax.parser import HTMLParser

from tests.conftest import FIXTURES_DIR
from vlrdevapi._team.info.parser import parse_team_info


def _load_html(team_id: int, mode: str) -> HTMLParser:
    path = (
        FIXTURES_DIR
        / "team"
        / str(team_id)
        / f"overview_{mode}.html"
    )
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


class TestParseTeamInfo:
    def test_parse_100_thieves(self):
        light_html = _load_html(120, "light")
        dark_html = _load_html(120, "dark")
        team = parse_team_info(light_html, dark_html)

        assert team.name == "100 Thieves"
        assert team.tag == "100T"
        assert team.country == "United States"
        assert team.is_active is True
        assert team.light_logo_url.startswith("https://")
        assert team.dark_logo_url.startswith("https://")
        assert team.light_logo_url != team.dark_logo_url
        assert team.socials is not None and len(team.socials) > 0
        # Add more assertions as needed

