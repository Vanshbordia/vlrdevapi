import pytest

import vlrdevapi
from vlrdevapi.exceptions import ValidationError


def _news_page_html(count: int = 2) -> str:
    items = "".join(
        f"""
        <a class="wf-module-item mod-first" href="/{i}/news-{i}">
            <div style="flex:1;">
                <div style="font-weight:700;">News {i}</div>
                <div style="font-size:13px;">Subtitle {i}</div>
                <div class="ge-text-light">
                    <i class="flag mod-us"></i>
                    <span>&bull;</span>
                    August {i}, 2026
                    <span>&bull;</span>
                    by author{i}
                </div>
            </div>
        </a>
        """
        for i in range(1, count + 1)
    )
    return f"""
    <html><body>
    <div class="wf-card">{items}</div>
    </body></html>
    """


class TestSyncNews:
    def test_news_default(self, mock_vlr):
        mock_vlr.get("/news").respond(200, text=_news_page_html())

        result = vlrdevapi.news()

        assert hasattr(result, "news")
        assert hasattr(result, "has_next_page")
        assert len(result.news) == 2
        assert result.news[0].id == 1
        assert result.news[0].title == "News 1"

    def test_news_page_2(self, mock_vlr):
        mock_vlr.get("/news/", params={"page": "2"}).respond(200, text=_news_page_html(1))

        result = vlrdevapi.news(page=2)

        assert len(result.news) == 1

    def test_news_invalid_page(self):
        with pytest.raises(ValidationError):
            vlrdevapi.news(page=0)
