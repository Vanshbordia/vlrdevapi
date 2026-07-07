from unittest.mock import patch

import pytest
from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
import vlrdevapi


_EVENTS_FIXTURE = HTMLParser(load_fixture("events", "events.html"))
_EVENTS_VCT_FIXTURE = HTMLParser(load_fixture("events", "events_region_26_americas_tier_60_vct.html"))
_EVENTS_AMERICAS_FIXTURE = HTMLParser(load_fixture("events", "events_region_26_americas.html"))
_EVENTS_EMEA_FIXTURE = HTMLParser(load_fixture("events", "events_region_27_emea.html"))


def _make_page(page: int, total: int, events_per_page: int = 2, status: str = "upcoming") -> HTMLParser:
    """Build an HTML page with the given number of events and pagination."""
    event_items = ""
    for i in range(events_per_page):
        eid = (page - 1) * events_per_page + i + 1
        event_items += f"""
        <a class="event-item" href="/event/{eid}/e{eid}">
          <div class="event-item-title">Event {eid}</div>
          <div class="event-item-desc-item-status mod-{status}">{status}</div>
        </a>"""

    buttons = "".join(
        f'<span class="btn mod-page{" mod-active" if p == page else ""}">{p}</span>'
        for p in range(1, total + 1)
    )

    return HTMLParser(f"""
    <html><body>
    <div class="events-container-col">
      <div class="wf-label mod-large">events</div>
      {event_items}
    </div>
    <div class="action-container-pages">{buttons}</div>
    </body></html>
    """)


class TestSyncModuleLevel:
    def test_event_list_default(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list()
        assert result is not None
        assert hasattr(result, "events")
        assert hasattr(result, "filters")
        assert hasattr(result, "pagination")
        assert isinstance(result.events, list)
        assert len(result.events) > 0

    def test_event_list_with_filters(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_VCT_FIXTURE):
            result = vlrdevapi.event.list(tier="vct", region="all", status="ongoing")
        assert result is not None
        assert result.filters.tier == "vct"
        assert result.filters.region == "all"
        assert result.filters.status == "ongoing"

    def test_event_list_pagination(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(page=1)
        assert result.pagination.current_page == 1
        assert result.pagination.total_pages >= 1
        assert isinstance(result.pagination.has_next, bool)
        assert isinstance(result.pagination.has_prev, bool)

    def test_event_list_tier_filter(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(tier="vct")
        assert result.filters.tier == "vct"

    def test_event_list_region_filter(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_AMERICAS_FIXTURE):
            result = vlrdevapi.event.list(region="americas")
        assert result.filters.region == "americas"

    def test_event_list_status_filter_completed(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(status="completed")
        assert result.filters.status == "completed"

    def test_event_list_status_filter_upcoming(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(status="upcoming")
        assert result.filters.status == "upcoming"


class TestSyncWithClient:
    def test_event_list_curried(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            with vlrdevapi.VLRClient() as client:
                result = client.event.list()
        assert result is not None
        assert len(result.events) > 0

    def test_event_list_direct(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_EMEA_FIXTURE):
            with vlrdevapi.VLRClient() as client:
                result = client.event.list(tier="vct", region="emea")
        assert result is not None
        assert result.filters.tier == "vct"
        assert result.filters.region == "emea"


class TestEventListValidation:
    def test_invalid_tier(self):
        with pytest.raises(vlrdevapi.exceptions.ValidationError):
            vlrdevapi.event.list(tier="invalid")

    def test_invalid_region(self):
        with pytest.raises(vlrdevapi.exceptions.ValidationError):
            vlrdevapi.event.list(region="invalid")

    def test_valid_tier_values(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(tier="vct")
        assert result.filters.tier == "vct"

        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(tier="gc")
        assert result.filters.tier == "gc"

    def test_valid_region_values(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_AMERICAS_FIXTURE):
            result = vlrdevapi.event.list(region="americas")
        assert result.filters.region == "americas"

        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_EMEA_FIXTURE):
            result = vlrdevapi.event.list(region="emea")
        assert result.filters.region == "emea"

    def test_invalid_page(self):
        with pytest.raises(ValueError, match="page must be a positive integer"):
            vlrdevapi.event.list(page=0)

    def test_invalid_page_negative(self):
        with pytest.raises(ValueError, match="page must be a positive integer"):
            vlrdevapi.event.list(page=-1)


class TestEventListDataStructure:
    def test_event_item_structure(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list()
        if result.events:
            event = result.events[0]
            assert hasattr(event, "id")
            assert hasattr(event, "name")
            assert hasattr(event, "status")
            assert hasattr(event, "prize")
            assert hasattr(event, "start_date")
            assert hasattr(event, "end_date")
            assert hasattr(event, "region")
            assert hasattr(event, "image_url")
            assert hasattr(event, "url")
            assert event.id > 0
            assert event.name != ""
            assert event.status in ["ongoing", "upcoming", "completed"]

    def test_prize_structure(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list()
        for event in result.events:
            if event.prize is not None:
                assert hasattr(event.prize, "amount")
                assert hasattr(event.prize, "currency_symbol")
                assert hasattr(event.prize, "currency_code")
                assert hasattr(event.prize, "is_tbd")
                assert hasattr(event.prize, "raw_text")

    def test_filters_structure(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list(tier="vct", region="americas", status="ongoing", page=1)
        assert result.filters.tier == "vct"
        assert result.filters.region == "americas"
        assert result.filters.status == "ongoing"
        assert result.filters.page == 1

    def test_pagination_structure(self):
        with patch("vlrdevapi._base.fetch_sync", return_value=_EVENTS_FIXTURE):
            result = vlrdevapi.event.list()
        pagination = result.pagination
        assert hasattr(pagination, "current_page")
        assert hasattr(pagination, "total_pages")
        assert hasattr(pagination, "has_next")
        assert hasattr(pagination, "has_prev")
        assert pagination.current_page >= 1
        assert pagination.total_pages >= 1
        assert isinstance(pagination.has_next, bool)
        assert isinstance(pagination.has_prev, bool)


class TestEventListReturnAll:
    def test_return_all_combines_pages(self):
        """Test return_all=True combines events from all pages."""
        pages = [_make_page(1, 3), _make_page(2, 3), _make_page(3, 3)]
        with patch("vlrdevapi._base.fetch_sync", side_effect=pages):
            result = vlrdevapi.event.list(return_all=True)
        assert len(result.events) == 6
        assert result.events[0].id == 1
        assert result.events[5].id == 6

    def test_return_all_with_status_filter(self):
        """Test return_all=True with status filter."""
        pages = [_make_page(1, 2, status="ongoing"), _make_page(2, 2, status="completed")]
        with patch("vlrdevapi._base.fetch_sync", side_effect=pages):
            result = vlrdevapi.event.list(return_all=True, status="ongoing")
        assert len(result.events) == 2
        assert all(e.status == "ongoing" for e in result.events)

    def test_return_all_max_page(self):
        """Test max_page limits pages fetched."""
        pages = [_make_page(1, 5), _make_page(2, 5)]
        with patch("vlrdevapi._base.fetch_sync", side_effect=pages):
            result = vlrdevapi.event.list(return_all=True, max_page=1)
        assert len(result.events) == 2
        assert all(e.id in (1, 2) for e in result.events)

    def test_return_all_with_tier_and_region(self):
        """Test return_all=True with tier and region filters."""
        pages = [_make_page(1, 1), _make_page(1, 1)]
        with patch("vlrdevapi._base.fetch_sync", side_effect=pages):
            result = vlrdevapi.event.list(return_all=True, tier="vct", region="emea")
        assert result.filters.tier == "vct"
        assert result.filters.region == "emea"

    def test_return_all_single_page(self):
        """Test return_all=True with a single page of results."""
        pages = [_make_page(1, 1)]
        with patch("vlrdevapi._base.fetch_sync", side_effect=pages):
            result = vlrdevapi.event.list(return_all=True)
        assert len(result.events) == 2
        assert result.has_next_page is False

    def test_return_all_respects_max_page_zero(self):
        """Test max_page=0 means no limit (fetch all pages)."""
        pages = [_make_page(1, 3), _make_page(2, 3), _make_page(3, 3)]
        with patch("vlrdevapi._base.fetch_sync", side_effect=pages):
            result = vlrdevapi.event.list(return_all=True, max_page=0)
        assert len(result.events) == 6
