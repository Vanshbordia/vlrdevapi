from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from selectolax.parser import HTMLParser

from tests.conftest import load_fixture
from vlrdevapi._news.article.parser import html_to_markdown, parse_news_article
from vlrdevapi._news.list.parser import _parse_news_item, parse_news_page


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


def _article_card_html(datetime_attr: str) -> str:
    return f"""
    <html>
    <head><link rel="canonical" href="https://www.vlr.gg/123/some-article"></head>
    <body>
    <div class="wf-card mod-article">
        <h1 class="wf-title mod-article-title">Some Article</h1>
        <time class="js-date-toggle" datetime="{datetime_attr}"></time>
        <div class="article-body"><p>Body</p></div>
    </div>
    </body>
    </html>
    """


def _body_node(inner_html: str) -> HTMLParser:
    return HTMLParser(f"<div>{inner_html}</div>").css_first("div")


class TestParseNewsItem:
    def test_full_item(self):
        html = HTMLParser(_item_html())
        item = html.css_first("a.wf-module-item")

        news = _parse_news_item(item)

        assert news is not None
        assert news.id == 734100
        assert (
            news.link
            == "/734100/gen-g-global-varrel-prx-bypass-pacific-stage-2-play-ins"
        )
        assert (
            news.title == "Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins"
        )
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
        assert (
            news.title == "Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins"
        )
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

    def test_no_next_page_on_last_page(self):
        html_content = """
        <div class="action-container-pages">
            <a class="btn mod-page" href="/news">1</a>
            <a class="btn mod-page" href="/news/?page=123">123</a>
            <a class="btn mod-page" href="/news/?page=124">124</a>
            <a class="btn mod-page" href="/news/?page=125">125</a>
            <span class="btn mod-page mod-active">126</span>
        </div>
        """
        html = HTMLParser(html_content)
        result = parse_news_page(html)

        assert result.page_number == 126
        assert result.has_next_page is False


class TestParseNewsFixture:
    def test_live_page_1(self):
        html = HTMLParser(load_fixture("news", "news.html"))
        result = parse_news_page(html)

        assert len(result.news) == 30
        assert result.page_number == 1
        assert result.has_next_page is True
        first = result.news[0]
        assert first.id > 0
        assert first.link.startswith("/")
        assert first.title != ""
        assert first.country_name != ""
        assert first.date is not None
        assert first.author != ""

    def test_live_last_page(self):
        html = HTMLParser(load_fixture("news", "news_page126.html"))
        result = parse_news_page(html)

        assert len(result.news) > 0
        assert result.page_number == 126
        assert result.has_next_page is False

    def test_out_of_range_page_has_no_items(self):
        html = HTMLParser(load_fixture("news", "news_page176.html"))
        result = parse_news_page(html)

        assert result.news == []


class TestParseNewsArticle:
    def test_fixture_article(self):
        html = HTMLParser(load_fixture("news", "article_734100.html"))
        article = parse_news_article(html)

        assert article.id == 734100
        assert (
            article.title
            == "Gen.G, Global, VARREL, PRX bypass Pacific Stage 2 Play-Ins"
        )
        assert article.author == "jenopelle"
        assert article.date is not None
        assert article.date.tzinfo is UTC
        assert article.event_name == "VCT 2026: Pacific Stage 2"
        assert (
            article.event_link
            == "https://www.vlr.gg/event/2776/vct-2026-pacific-stage-2"
        )
        assert article.content != ""
        assert "Pacific Stage 2 has drawn to a close" in article.content
        assert "Rank #" not in article.content
        assert "Meiy" not in article.content

    def test_fixture_article_markdown(self):
        html = HTMLParser(load_fixture("news", "article_734100.html"))
        article = parse_news_article(html)

        assert article.content_md != ""
        assert "## 1. Gen.G (5-0)" in article.content_md
        assert "# Up Next" in article.content_md
        assert (
            "- [DetonatioN FocusMe](https://www.vlr.gg/team/278/detonation-focusme)"
            in article.content_md
        )
        assert (
            "[Pacific Stage 2](https://www.vlr.gg/event/2776/vct-2026-pacific-stage-2/group-stage)"
            in article.content_md
        )
        assert "*It's an eco, but my goodness, Karon.*" in article.content_md
        assert article.content_md.startswith(
            "The [Pacific Stage 2](https://www.vlr.gg/event/2776/vct-2026-pacific-stage-2/group-stage) has drawn to a close"
        )
        assert "Rank #" not in article.content_md
        assert "Meiy" not in article.content_md
        assert "parent=www.vlr.gg" not in article.content_md
        assert "](/" not in article.content_md
        assert "clips.twitch.tv/embed" not in article.content_md
        assert (
            "- [DetonatioN FocusMe](https://www.vlr.gg/team/278/detonation-focusme) "
            "[2-0](https://www.vlr.gg/698910/team-secret-vs-detonation-focusme-vct-2026-pacific-stage-2-w4) "
            "[Team Secret](https://www.vlr.gg/team/6199/team-secret)"
            in article.content_md
        )
        assert (
            "[Watch clip](https://clips.twitch.tv/RamshackleOnerousKleeMingLee-SZcLugk71ukapuXF)"
            in article.content_md
        )

    def test_empty_html(self):
        html = HTMLParser("<html><body></body></html>")
        article = parse_news_article(html)

        assert article.id == 0
        assert article.title == ""
        assert article.author == ""
        assert article.date is None
        assert article.event_name == ""
        assert article.event_link == ""
        assert article.content == ""
        assert article.content_md == ""


class TestParseNewsArticle720033:
    def test_fixture_article_720033(self):
        html = HTMLParser(load_fixture("news", "article_720033.html"))
        article = parse_news_article(html)

        assert article.id == 720033
        assert article.title == "Americas' recent victors start strong in week 1"
        assert article.author == "CongoBat"
        assert article.date is not None
        assert article.date.tzinfo is UTC
        assert article.event_name == "VCT 2026: Americas Stage 2"
        assert (
            article.event_link
            == "https://www.vlr.gg/event/2977/vct-2026-americas-stage-2"
        )
        assert article.content != ""
        assert "back breaking clutch" in article.content

    def test_fixture_article_720033_markdown(self):
        html = HTMLParser(load_fixture("news", "article_720033.html"))
        article = parse_news_article(html)

        assert article.content_md != ""
        assert (
            "*A back breaking clutch out of [mada](https://www.vlr.gg/player/5132/mada) seals MIBR's fate.*"
            in article.content_md
        )
        assert "[johnqt](https://www.vlr.gg/player/1265/johnqt)" in article.content_md
        assert "[Marved](https://www.vlr.gg/player/263/marved)" in article.content_md
        assert (
            "*Leviatán have not skipped a beat since [Masters London](https://www.vlr.gg/event/2765/valorant-masters-london-2026/playoffs).*"
            in article.content_md
        )
        assert (
            "[Americas Stage 2](https://www.vlr.gg/event/2977/vct-2026-americas-stage-2/group-stage)"
            in article.content_md
        )
        assert (
            "[Watch clip](https://clips.twitch.tv/GoodStupidHabaneroWutFace-ku1N4hHLzSbxIYoS)"
            in article.content_md
        )
        assert (
            "[Watch clip](https://clips.twitch.tv/StormySuccessfulElkStoneLightning-Lhfah0EgaCAepfVq)"
            in article.content_md
        )
        assert (
            "[Watch clip](https://clips.twitch.tv/CallousComfortableMagpiePraiseIt-ENcoD2w_HxOO87Rn)"
            in article.content_md
        )
        assert (
            "[Watch clip](https://clips.twitch.tv/AlertAlertWhaleYee-w2hkUywZhve14f2h)"
            in article.content_md
        )
        assert "clips.twitch.tv/embed" not in article.content_md
        assert "parent=www.vlr.gg" not in article.content_md
        assert "](/" not in article.content_md
        assert (
            "Sentinels managed to clutch a win over Cloud9 despite being without their IGL"
            in article.content_md
        )


class TestHtmlToMarkdown:
    def test_nested_list(self):
        md = html_to_markdown(
            _body_node(
                "<ul><li>Top<ul><li>Sub A</li><li>Sub B</li></ul></li><li>Other</li></ul>"
            )
        )

        assert md == "- Top\n  - Sub A\n  - Sub B\n- Other"

    def test_table(self):
        md = html_to_markdown(
            _body_node(
                "<table><tr><th>Team</th><th>W</th><th>L</th></tr>"
                "<tr><td>PRX</td><td>5</td><td>0</td></tr></table>"
            )
        )

        assert md == "| Team | W | L |\n| --- | --- | --- |\n| PRX | 5 | 0 |"

    def test_code_preserves_whitespace(self):
        md = html_to_markdown(_body_node("<p>Use <code>a  b   c</code> here.</p>"))

        assert "`a  b   c`" in md

    def test_code_with_backtick_uses_double_backticks(self):
        md = html_to_markdown(_body_node("<p><code>a`b</code></p>"))

        assert "``a`b``" in md

    def test_www_link_upgraded_to_https(self):
        md = html_to_markdown(
            _body_node('<p><a href="www.example.com/x">Example</a></p>')
        )

        assert "[Example](https://www.example.com/x)" in md

    def test_inline_whitespace_collapses_but_br_kept(self):
        md = html_to_markdown(_body_node("<p>a  b<br>c</p>"))

        assert md == "a b  \nc"


class TestParseNewsArticleDate:
    def test_offset_aware_datetime_converted_to_utc(self):
        article = parse_news_article(
            HTMLParser(_article_card_html("2026-08-10T04:16:27+05:30"))
        )

        assert article.date == datetime(2026, 8, 9, 22, 46, 27, tzinfo=UTC)

    def test_naive_datetime_defaults_to_utc(self):
        article = parse_news_article(
            HTMLParser(_article_card_html("2026-08-10T04:16:27"))
        )

        assert article.date == datetime(2026, 8, 10, 4, 16, 27, tzinfo=UTC)

    def test_naive_datetime_with_source_tz(self):
        article = parse_news_article(
            HTMLParser(_article_card_html("2026-08-10T04:16:27")),
            source_tz=ZoneInfo("America/New_York"),
        )

        assert article.date == datetime(2026, 8, 10, 8, 16, 27, tzinfo=UTC)

    def test_unparseable_datetime_returns_none(self):
        article = parse_news_article(HTMLParser(_article_card_html("not a date")))

        assert article.date is None
