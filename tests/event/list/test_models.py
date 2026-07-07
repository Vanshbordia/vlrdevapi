import pytest
from datetime import date

from vlrdevapi._event.list.models import (
    EventListItem,
    EventList,
    EventListFilters,
    EventListPagination,
)
from vlrdevapi._event.info.models import EventPrize


class TestEventListItem:
    def test_creation_minimal(self):
        """Test creating EventListItem with minimal data."""
        item = EventListItem(id=123, name="Test Event", status="ongoing")
        assert item.id == 123
        assert item.name == "Test Event"
        assert item.status == "ongoing"
        assert item.prize is None
        assert item.start_date is None
        assert item.end_date is None
        assert item.region == ""
        assert item.image_url == ""
        assert item.url == ""

    def test_creation_full(self):
        """Test creating EventListItem with all fields."""
        prize = EventPrize(amount=50000, currency_symbol="$", is_tbd=False)
        start_date = date(2026, 4, 1)
        end_date = date(2026, 4, 5)

        item = EventListItem(
            id=456,
            name="Full Test Event",
            status="upcoming",
            prize=prize,
            start_date=start_date,
            end_date=end_date,
            region="United States",
            image_url="https://example.com/image.png",
            url="https://vlr.gg/event/456",
        )

        assert item.id == 456
        assert item.name == "Full Test Event"
        assert item.status == "upcoming"
        assert item.prize is not None
        assert item.prize.amount == 50000
        assert item.start_date == start_date
        assert item.end_date == end_date
        assert item.region == "United States"
        assert item.image_url == "https://example.com/image.png"
        assert item.url == "https://vlr.gg/event/456"

    def test_status_validation(self):
        """Test that invalid status raises validation error."""
        with pytest.raises(ValueError):
            EventListItem(id=1, name="Test", status="invalid")  # type: ignore

    def test_serialization(self):
        """Test JSON serialization."""
        item = EventListItem(
            id=789, name="Serializable Event", status="completed", region="Germany"
        )

        data = item.model_dump()
        assert data["id"] == 789
        assert data["name"] == "Serializable Event"
        assert data["status"] == "completed"
        assert data["region"] == "Germany"

    def test_deserialization(self):
        """Test JSON deserialization."""
        data = {
            "id": 999,
            "name": "Deserialized Event",
            "status": "ongoing",
            "region": "France",
            "prize": None,
            "start_date": None,
            "end_date": None,
            "image_url": "",
            "url": "",
        }

        item = EventListItem.model_validate(data)
        assert item.id == 999
        assert item.name == "Deserialized Event"
        assert item.status == "ongoing"
        assert item.region == "France"


class TestEventListPagination:
    def test_creation(self):
        """Test EventListPagination creation."""
        pagination = EventListPagination(current_page=2, total_pages=5)

        assert pagination.current_page == 2
        assert pagination.total_pages == 5
        assert pagination.has_next is True  # computed property
        assert pagination.has_prev is True  # computed property

    def test_defaults(self):
        """Test EventListPagination defaults."""
        pagination = EventListPagination()
        assert pagination.current_page == 1
        assert pagination.total_pages == 1
        assert pagination.has_next is False
        assert pagination.has_prev is False

    def test_single_page(self):
        """Test single page scenario."""
        pagination = EventListPagination(current_page=1, total_pages=1)
        assert pagination.has_next is False
        assert pagination.has_prev is False

    def test_first_page_multi_page(self):
        """Test first page of multi-page result."""
        pagination = EventListPagination(current_page=1, total_pages=3)
        assert pagination.has_next is True
        assert pagination.has_prev is False

    def test_last_page(self):
        """Test last page scenario."""
        pagination = EventListPagination(current_page=5, total_pages=5)
        assert pagination.has_next is False
        assert pagination.has_prev is True

    def test_middle_page(self):
        """Test middle page scenario."""
        pagination = EventListPagination(current_page=3, total_pages=7)
        assert pagination.has_next is True
        assert pagination.has_prev is True


class TestEventListFilters:
    def test_creation(self):
        """Test EventListFilters creation."""
        filters = EventListFilters(
            tier="vct", region="americas", status="ongoing", page=2
        )

        assert filters.tier == "vct"
        assert filters.region == "americas"
        assert filters.status == "ongoing"
        assert filters.page == 2

    def test_defaults(self):
        """Test EventListFilters defaults."""
        filters = EventListFilters()
        assert filters.tier == "all"
        assert filters.region == "all"
        assert filters.status is None
        assert filters.page == 1


class TestEventList:
    def test_creation_full(self):
        """Test EventList creation with full data."""
        events = [
            EventListItem(id=1, name="Event 1", status="ongoing"),
            EventListItem(id=2, name="Event 2", status="upcoming"),
        ]

        filters = EventListFilters(tier="vct", region="emea", status=None, page=1)
        pagination = EventListPagination(current_page=1, total_pages=3)

        event_list = EventList(events=events, filters=filters, pagination=pagination)

        assert len(event_list.events) == 2
        assert event_list.events[0].id == 1
        assert event_list.events[1].id == 2
        assert event_list.filters.tier == "vct"
        assert event_list.filters.region == "emea"
        assert event_list.pagination.current_page == 1
        assert event_list.pagination.total_pages == 3

    def test_matches_synced_from_events(self):
        """Test matches is synced from events via model_validator."""
        events = [
            EventListItem(id=1, name="Event 1", status="ongoing"),
        ]
        filters = EventListFilters(tier="all", region="all", status=None, page=1)
        pagination = EventListPagination(current_page=1, total_pages=3)

        event_list = EventList(events=events, filters=filters, pagination=pagination)

        assert event_list.matches == event_list.events
        assert len(event_list.matches) == 1
        assert event_list.matches[0].id == 1

    def test_has_next_page_synced_from_pagination(self):
        """Test has_next_page is synced from pagination.has_next."""
        filters = EventListFilters(tier="all", region="all", status=None, page=1)

        # has_next = True
        pag = EventListPagination(current_page=1, total_pages=3)
        el = EventList(events=[], filters=filters, pagination=pag)
        assert el.has_next_page is True

        # has_next = False (last page)
        pag = EventListPagination(current_page=3, total_pages=3)
        el = EventList(events=[], filters=filters, pagination=pag)
        assert el.has_next_page is False

        # has_next = False (single page)
        pag = EventListPagination(current_page=1, total_pages=1)
        el = EventList(events=[], filters=filters, pagination=pag)
        assert el.has_next_page is False

    def test_creation_minimal(self):
        """Test EventList creation with minimal valid data."""
        filters = EventListFilters()
        pagination = EventListPagination()
        event_list = EventList(events=[], filters=filters, pagination=pagination)

        # Should work with default values
        assert len(event_list.events) == 0
        assert event_list.filters.tier == "all"
        assert event_list.pagination.current_page == 1

    def test_serialization(self):
        """Test EventList JSON serialization."""
        events = [EventListItem(id=1, name="Test", status="ongoing")]
        filters = EventListFilters(tier="vct", region="all", status=None, page=1)
        pagination = EventListPagination(current_page=1, total_pages=2)

        event_list = EventList(events=events, filters=filters, pagination=pagination)

        data = event_list.model_dump()
        assert "events" in data
        assert "matches" in data
        assert "has_next_page" in data
        assert "filters" in data
        assert "pagination" in data
        assert len(data["events"]) == 1
        assert data["matches"] == data["events"]
        assert data["has_next_page"] is True
        assert data["filters"]["tier"] == "vct"
        assert data["pagination"]["current_page"] == 1

    def test_deserialization(self):
        """Test EventList JSON deserialization."""
        data = {
            "events": [
                {
                    "id": 123,
                    "name": "Test Event",
                    "status": "ongoing",
                    "prize": None,
                    "start_date": None,
                    "end_date": None,
                    "region": "",
                    "image_url": "",
                    "url": "",
                }
            ],
            "filters": {"tier": "all", "region": "all", "status": None, "page": 1},
            "pagination": {
                "current_page": 1,
                "total_pages": 1,
                "has_next": False,
                "has_prev": False,
            },
        }

        event_list = EventList.model_validate(data)
        assert len(event_list.events) == 1
        assert event_list.events[0].id == 123
        assert event_list.events[0].name == "Test Event"
        assert event_list.matches == event_list.events
        assert event_list.has_next_page is False
        assert event_list.filters.tier == "all"
        assert event_list.pagination.current_page == 1

