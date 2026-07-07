from pathlib import Path

import pytest
import respx

import vlrdevapi
from vlrdevapi import VLRClient

FIXTURES_DIR = Path(__file__).resolve().parent / "test_html"

_LIVE = False


def load_fixture(*path_parts: str) -> str:
    path = FIXTURES_DIR / Path(*path_parts)
    if not path.exists():
        raise FileNotFoundError(
            f"Fixture file not found: {path}. "
        )
    return path.read_text(encoding="utf-8")


def live_fetch(url: str, headers: dict | None = None) -> str:
    """Fetch HTML from VLR.gg."""
    import httpx
    resp = httpx.get(
        f"https://www.vlr.gg{url}",
        headers=headers or {},
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--live", action="store_true", help="Fetch live HTML instead of using fixtures")


def pytest_configure(config: pytest.Config) -> None:
    global _LIVE
    _LIVE = config.getoption("--live", default=False)


@pytest.fixture
def client():
    with VLRClient() as c:
        yield c


@pytest.fixture
def mock_vlr():
    with respx.mock(base_url="https://www.vlr.gg", assert_all_called=False) as m:
        yield m


@pytest.fixture(autouse=True)
def _reset_module_client():
    yield
    vlrdevapi._default_client = None
