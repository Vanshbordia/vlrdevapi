import inspect
from pathlib import Path

import httpx
import pytest
import respx

import vlrdevapi
from vlrdevapi import VLRClient

FIXTURES_DIR = Path(__file__).resolve().parent / "test_html"
LIVE_BASE = "https://www.vlr.gg"
_LIVE = False


def live_fetch(url: str, headers: dict | None = None) -> str:
    """Fetch HTML from VLR.gg during --live mode."""
    resp = httpx.get(f"{LIVE_BASE}{url}", headers=headers or {}, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    return resp.text


def load_fixture(*path_parts: str) -> str:
    if _LIVE:
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_code.co_name == "<module>":
            pytest.skip("in --live mode", allow_module_level=True)
        return ""
    path = FIXTURES_DIR / Path(*path_parts)
    if not path.exists():
        raise FileNotFoundError(
            f"Fixture file not found: {path}. "
            "Run with --live to use real HTTP requests instead."
        )
    return path.read_text(encoding="utf-8")


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Make real HTTP requests to vlr.gg instead of using local fixtures",
    )


def pytest_configure(config):
    global _LIVE
    _LIVE = config.getoption("--live")


class _NoopResponse:
    def respond(self, status, *, text=""):
        pass


class _NoopMock:
    """Stub that silently accepts mock setup calls so --live tests don't break."""

    def get(self, url, **kwargs):
        return _NoopResponse()


@pytest.fixture
def client():
    with VLRClient() as c:
        yield c


@pytest.fixture
def mock_vlr(request):
    if request.config.getoption("--live"):
        yield _NoopMock()
    else:
        with respx.mock(base_url="https://www.vlr.gg", assert_all_called=False) as m:
            yield m


@pytest.fixture(autouse=True)
def _reset_module_client():
    yield
    vlrdevapi._default_client = None
