import pytest

import vlrdevapi
from tests.conftest import load_fixture
from vlrdevapi.exceptions import NotFoundError, ValidationError


class TestSyncNews:
    def test_news_default(self, mock_vlr):
        mock_vlr.get("/news").respond(200, text=load_fixture("news", "news.html"))

        result = vlrdevapi.news()

        assert hasattr(result, "news")
        assert hasattr(result, "has_next_page")
        assert len(result.news) == 30
        assert result.page_number == 1
        assert result.has_next_page is True
        assert result.news[0].id > 0
        assert result.news[0].title != ""
        assert result.news[0].link.startswith("/")

    def test_news_page_2(self, mock_vlr):
        mock_vlr.get("/news/", params={"page": "2"}).respond(
            200, text=load_fixture("news", "news_page2.html")
        )

        result = vlrdevapi.news(page=2)

        assert len(result.news) == 30
        assert result.page_number == 2
        assert result.has_next_page is True

    def test_news_last_page_has_no_next(self, mock_vlr):
        mock_vlr.get("/news/", params={"page": "126"}).respond(
            200, text=load_fixture("news", "news_page126.html")
        )

        result = vlrdevapi.news(page=126)

        assert result.page_number == 126
        assert result.has_next_page is False
        assert len(result.news) > 0

    def test_news_invalid_page(self):
        with pytest.raises(ValidationError):
            vlrdevapi.news(page=0)

    def test_news_out_of_range_page_raises(self, mock_vlr):
        mock_vlr.get("/news/", params={"page": "176"}).respond(
            200, text=load_fixture("news", "news_page176.html")
        )

        with pytest.raises(NotFoundError):
            vlrdevapi.news(page=176)

    def test_news_article(self, mock_vlr):
        mock_vlr.get("/734100").respond(
            200, text=load_fixture("news", "article_734100.html")
        )

        result = vlrdevapi.news.article(734100)

        assert result.id == 734100
        assert result.title != ""
        assert result.author != ""
        assert result.event_name != ""
        assert result.content != ""
        assert result.content_md != ""

    def test_news_article_invalid_id(self):
        with pytest.raises(ValidationError):
            vlrdevapi.news.article(0)

    def test_news_article_missing_raises_not_found(self, mock_vlr):
        mock_vlr.get("/720034").respond(
            200, text="<html><body><p>Not an article page</p></body></html>"
        )

        with pytest.raises(NotFoundError):
            vlrdevapi.news.article(720034)
