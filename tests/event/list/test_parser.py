from selectolax.parser import HTMLParser

from vlrdevapi._event.list.parser import (
    parse_event_list,
    _detect_section_status,
    _extract_event_id,
    _extract_status,
    _parse_prize,
    _parse_pagination,
)


class TestParseEventList:
    def test_empty_html(self):
        """Test parsing with empty HTML."""
        html = HTMLParser("<html><body></body></html>")
        result = parse_event_list(
            html, {"tier": "all", "region": "all", "status": None, "page": 1}
        )

        assert result is not None
        assert len(result.events) == 0
        assert result.filters.tier == "all"
        assert result.filters.region == "all"
        assert result.filters.status is None
        assert result.filters.page == 1

    def test_single_event(self):
        """Test parsing single event."""
        html_content = """
        <html><body>
        <div class="events-container-col">
        <div class="wf-label mod-large mod-upcoming">upcoming events</div>
        <a class="event-item" href="/event/123/test-event">
        <div class="event-item-title">Test Event</div>
        <div class="event-item-desc-item-status mod-ongoing">ongoing</div>
        <div class="event-item-desc-item mod-prize">$10,000<div class="event-item-desc-item-label">Prize Pool</div></div>
        <div class="event-item-desc-item mod-dates">Apr 1—May 18<div class="event-item-desc-item-label">Dates</div></div>
        <div class="event-item-desc-item mod-location"><i class="flag mod-us"></i></div>
        <div class="event-item-thumb"><img src="//owcdn.net/img/test.png"></div>
        </a>
        </div>
        </body></html>
        """
        html = HTMLParser(html_content)
        result = parse_event_list(
            html, {"tier": "all", "region": "all", "status": None, "page": 1}
        )

        assert len(result.events) == 1
        event = result.events[0]
        assert event.id == 123
        assert event.name == "Test Event"
        assert event.status == "ongoing"
        assert event.prize is not None
        assert event.prize.amount == 10000
        assert event.prize.currency_symbol == "$"
        assert event.start_date is not None
        assert event.end_date is not None
        assert event.region == "United States"
        assert event.image_url == "https://owcdn.net/img/test.png"
        assert event.url == "https://www.vlr.gg/event/123/test-event"

    def test_status_filtering(self):
        """Test status filtering."""
        html_content = """
        <html><body>
        <div class="events-container-col">
        <a class="event-item" href="/event/1/e1">
        <div class="event-item-desc-item-status mod-ongoing">ongoing</div>
        </a>
        <a class="event-item" href="/event/2/e2">
        <div class="event-item-desc-item-status mod-upcoming">upcoming</div>
        </a>
        <a class="event-item" href="/event/3/e3">
        <div class="event-item-desc-item-status mod-completed">completed</div>
        </a>
        </div>
        </body></html>
        """
        html = HTMLParser(html_content)

        # Test filtering for ongoing
        result = parse_event_list(
            html, {"tier": "all", "region": "all", "status": "ongoing", "page": 1}
        )
        assert len(result.events) == 1
        assert result.events[0].status == "ongoing"

        # Test filtering for upcoming
        result = parse_event_list(
            html, {"tier": "all", "region": "all", "status": "upcoming", "page": 1}
        )
        assert len(result.events) == 1
        assert result.events[0].status == "upcoming"

        # Test no filtering
        result = parse_event_list(
            html, {"tier": "all", "region": "all", "status": None, "page": 1}
        )
        assert len(result.events) == 3

    def test_pagination_parsing(self):
        """Test pagination parsing."""
        html_content = """
        <html><body>
        <div class="action-container-pages">
        <a href="/events/?page=1" class="btn mod-page">1</a>
        <span class="btn mod-page mod-active">2</span>
        <a href="/events/?page=3" class="btn mod-page">3</a>
        <a href="/events/?page=4" class="btn mod-page">4</a>
        <a href="/events/?page=5" class="btn mod-page">5</a>
        </div>
        </body></html>
        """
        html = HTMLParser(html_content)
        result = parse_event_list(
            html, {"tier": "all", "region": "all", "status": None, "page": 1}
        )

        assert result.pagination.current_page == 2
        assert result.pagination.total_pages == 5
        assert result.pagination.has_next is True
        assert result.pagination.has_prev is True


class TestDetectSectionStatus:
    def test_upcoming_section(self):
        """Test detecting upcoming section."""
        html = HTMLParser(
            '<div class="wf-label mod-large mod-upcoming">upcoming events</div>'
        )
        div = html.css_first("div")
        assert div is not None
        result = _detect_section_status(div)
        assert result == "upcoming"

    def test_completed_section(self):
        """Test detecting completed section."""
        html = HTMLParser(
            '<div class="wf-label mod-large mod-completed">completed events</div>'
        )
        div = html.css_first("div")
        assert div is not None
        result = _detect_section_status(div)
        assert result == "completed"

    def test_ongoing_section(self):
        """Test detecting ongoing section."""
        html = HTMLParser(
            '<div class="wf-label mod-large mod-ongoing">ongoing events</div>'
        )
        div = html.css_first("div")
        assert div is not None
        result = _detect_section_status(div)
        assert result == "ongoing"

    def test_no_mod_class(self):
        """Test default when no mod class."""
        html = HTMLParser('<div class="wf-label mod-large">events</div>')
        div = html.css_first("div")
        assert div is not None
        result = _detect_section_status(div)
        assert result == "upcoming"

    def test_no_label(self):
        """Test when no label element."""
        html = HTMLParser("<div>No label</div>")
        div = html.css_first("div")
        assert div is not None
        result = _detect_section_status(div)
        assert result == "upcoming"


class TestExtractEventId:
    def test_valid_href(self):
        """Test extracting ID from valid href."""
        assert _extract_event_id("/event/123/test-event") == 123
        assert _extract_event_id("/event/456/") == 456
        assert _extract_event_id("/event/789?tab=overview") == 789

    def test_invalid_href(self):
        """Test extracting ID from invalid href."""
        assert _extract_event_id("/not-event/123") is None
        assert _extract_event_id("/event/abc/invalid") is None
        assert _extract_event_id("") is None
        assert _extract_event_id("invalid") is None


class TestExtractStatus:
    def test_mod_ongoing(self):
        """Test extracting ongoing status."""
        html = HTMLParser(
            '<span class="event-item-desc-item-status mod-ongoing">ongoing</span>'
        )
        span = html.css_first("span")
        result = _extract_status(span, "fallback")  # type: ignore
        assert result == "ongoing"

    def test_mod_upcoming(self):
        """Test extracting upcoming status."""
        html = HTMLParser(
            '<span class="event-item-desc-item-status mod-upcoming">upcoming</span>'
        )
        span = html.css_first("span")
        result = _extract_status(span, "fallback")  # type: ignore
        assert result == "upcoming"

    def test_mod_completed(self):
        """Test extracting completed status."""
        html = HTMLParser(
            '<span class="event-item-desc-item-status mod-completed">completed</span>'
        )
        span = html.css_first("span")
        result = _extract_status(span, "fallback")  # type: ignore
        assert result == "completed"

    def test_no_mod_class(self):
        """Test fallback when no mod class."""
        html = HTMLParser('<span class="event-item-desc-item-status"></span>')
        span = html.css_first("span")
        assert span is not None
        result = _extract_status(span, "fallback_status")  # type: ignore
        assert result == "upcoming"  # function now defaults to "upcoming"

    def test_no_span(self):
        """Test with no span element."""
        result = _extract_status(None, "ongoing")
        assert result == "ongoing"  # should return valid section_status

        result = _extract_status(None, "invalid_status")  # type: ignore
        assert result == "upcoming"  # should default to "upcoming" for invalid status


class TestParsePrize:
    def test_dollar_amount(self):
        """Test parsing dollar amount."""
        html = HTMLParser(
            '<div class="event-item-desc-item mod-prize">$10,000<div class="event-item-desc-item-label">Prize Pool</div></div>'
        )
        el = html.css_first("div")
        prize = _parse_prize(el)
        assert prize is not None
        assert prize.amount == 10000
        assert prize.currency_symbol == "$"
        assert prize.is_tbd is False

    def test_tbd_prize(self):
        """Test parsing TBD prize."""
        html = HTMLParser(
            '<div class="event-item-desc-item mod-prize">TBD<div class="event-item-desc-item-label">Prize Pool</div></div>'
        )
        el = html.css_first("div")
        prize = _parse_prize(el)
        assert prize is not None
        assert prize.is_tbd is True
        assert prize.amount is None

    def test_zero_prize(self):
        """Test parsing $0 prize."""
        html = HTMLParser(
            '<div class="event-item-desc-item mod-prize">$0<div class="event-item-desc-item-label">Prize Pool</div></div>'
        )
        el = html.css_first("div")
        prize = _parse_prize(el)
        assert prize is not None
        assert prize.amount == 0
        assert prize.currency_symbol == "$"

    def test_multi_currency(self):
        """Test parsing multi-currency prize."""
        html = HTMLParser(
            '<div class="event-item-desc-item mod-prize">¥1,234,567 JPY ~ $12,345 USD<div class="event-item-desc-item-label">Prize Pool</div></div>'
        )
        el = html.css_first("div")
        prize = _parse_prize(el)
        assert prize is not None
        assert prize.amount == 1234567
        assert prize.currency_symbol == "¥"
        assert prize.currency_code == "JPY"
        # No conversion logic for list view
        assert prize.converted_amount is None

    def test_no_prize_element(self):
        """Test with no prize element."""
        prize = _parse_prize(None)
        assert prize is None


class TestParsePagination:
    def test_basic_pagination(self):
        """Test basic pagination parsing."""
        html = HTMLParser("""
        <div class="action-container-pages">
        <a href="/events/?page=1" class="btn mod-page">1</a>
        <span class="btn mod-page mod-active">2</span>
        <a href="/events/?page=3" class="btn mod-page">3</a>
        </div>
        """)
        result = _parse_pagination(html)
        assert result.current_page == 2
        assert result.total_pages == 3
        assert result.has_next is True
        assert result.has_prev is True

    def test_single_page(self):
        """Test single page pagination."""
        html = HTMLParser(
            '<div class="action-container-pages"><span class="btn mod-page mod-active">1</span></div>'
        )
        result = _parse_pagination(html)
        assert result.current_page == 1
        assert result.total_pages == 1
        assert result.has_next is False
        assert result.has_prev is False

    def test_first_page(self):
        """Test first page of multi-page."""
        html = HTMLParser("""
        <div class="action-container-pages">
        <span class="btn mod-page mod-active">1</span>
        <a href="/events/?page=2" class="btn mod-page">2</a>
        <a href="/events/?page=3" class="btn mod-page">3</a>
        </div>
        """)
        result = _parse_pagination(html)
        assert result.current_page == 1
        assert result.total_pages == 3
        assert result.has_next is True
        assert result.has_prev is False

    def test_last_page(self):
        """Test last page."""
        html = HTMLParser("""
        <div class="action-container-pages">
        <a href="/events/?page=1" class="btn mod-page">1</a>
        <a href="/events/?page=2" class="btn mod-page">2</a>
        <span class="btn mod-page mod-active">3</span>
        </div>
        """)
        result = _parse_pagination(html)
        assert result.current_page == 3
        assert result.total_pages == 3
        assert result.has_next is False
        assert result.has_prev is True

    def test_no_pagination(self):
        """Test with no pagination element."""
        html = HTMLParser("<div>No pagination</div>")
        result = _parse_pagination(html)
        assert result.current_page == 1
        assert result.total_pages == 1
        assert result.has_next is False
        assert result.has_prev is False

    def test_large_page_numbers(self):
        """Test with large page numbers."""
        html = HTMLParser("""
        <div class="action-container-pages">
        <a href="/events/?page=95" class="btn mod-page">95</a>
        <span class="btn mod-page mod-active">96</span>
        <a href="/events/?page=97" class="btn mod-page">97</a>
        <a href="/events/?page=100" class="btn mod-page">100</a>
        </div>
        """)
        result = _parse_pagination(html)
        assert result.current_page == 96
        assert result.total_pages == 100
        assert result.has_next is True
        assert result.has_prev is True

