from datetime import UTC, datetime

from selectolax.parser import HTMLParser

from vlrdevapi._news.parser import _parse_news_item, parse_news_page


def _item_html(
    href: str = "/734100/gen-g-global-varrel-prx-bypass-pacific-stage-2-play-ins",
    title: str = "Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins",
    subtitle: str = "Off to the Play-Ins!",
    country_code: str = "kr",
    date_text: str = "August 9, 2026",
    author: str = "jenopelle",
) -> str:
    return f"""
    <a class="wf-module-item mod-first" href="{href}">
        <div style="flex:1;">
            <div style="font-weight:700;">{title}</div>
            <div style="font-size:13px;">{subtitle}</div>
            <div class="ge-text-light">
                <i class="flag mod-{country_code}"></i>
                <span>&bull;</span>
                {date_text}
                <span>&bull;</span>
                by {author}
            </div>
        </div>
    </a>
    """


class TestParseNewsItem:
    def test_full_item(self):
        html = HTMLParser(_item_html())
        item = html.css_first("a.wf-module-item")

        news = _parse_news_item(item)

        assert news is not None
        assert news.id == 734100
        assert news.link == "/734100/gen-g-global-varrel-prx-bypass-pacific-stage-2-play-ins"
        assert news.title == "Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins"
        assert news.subtitle == "Off to the Play-Ins!"
        assert news.country_name == "South Korea"
        assert news.author == "jenopelle"
        assert news.date == datetime(2026, 8, 9, tzinfo=UTC)

    def test_item_without_subtitle(self):
        html_content = """
        <a class="wf-module-item" href="/1/only-title">
            <div style="flex:1;">
                <div style="font-weight:700;">Only Title</div>
                <div class="ge-text-light">
                    <i class="flag mod-us"></i>
                    <span>&bull;</span>
                    August 1, 2026
                </div>
            </div>
        </a>
        """
        html = HTMLParser(html_content)
        item = html.css_first("a.wf-module-item")

        news = _parse_news_item(item)

        assert news is not None
        assert news.id == 1
        assert news.title == "Only Title"
        assert news.subtitle == ""

    def test_item_with_unparseable_date_keeps_other_fields(self):
        html = HTMLParser(_item_html(date_text="not a date"))
        item = html.css_first("a.wf-module-item")

        news = _parse_news_item(item)

        assert news is not None
        assert news.title == "Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins"
        assert news.date is None


class TestParseNewsPage:
    def test_empty_html(self):
        html = HTMLParser("<html><body></body></html>")
        result = parse_news_page(html)

        assert result.news == []
        assert result.has_next_page is False

    def test_multiple_items(self):
        html_content = f"""
        <div class="wf-card">
            {_item_html(href="/1/first", title="First")}
            {_item_html(href="/2/second", title="Second")}
        </div>
        """
        html = HTMLParser(html_content)
        result = parse_news_page(html)

        assert len(result.news) == 2
        assert result.news[0].id == 1
        assert result.news[1].id == 2

    def test_has_next_page(self):
        html_content = """
        <div class="action-container-pages">
            <span class="btn mod-page mod-active">1</span>
            <a class="btn mod-page" href="/news/?page=2">2</a>
        </div>
        """
        html = HTMLParser(html_content)
        result = parse_news_page(html)

        assert result.has_next_page is True
