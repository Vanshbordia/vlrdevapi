from pathlib import Path

import pytest
import respx

import vlrdevapi
from vlrdevapi import VLRClient

FIXTURES_DIR = Path(__file__).resolve().parent / "test_html"


def load_fixture(*path_parts: str) -> str:
    return (FIXTURES_DIR / Path(*path_parts)).read_text(encoding="utf-8")


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Make real HTTP requests to vlr.gg instead of using local fixtures",
    )


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
