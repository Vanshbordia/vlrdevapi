from vlrdevapi._news.models import News, NewsPage


class TestNews:
    def test_defaults(self):
        news = News()
        assert news.id == 0
        assert news.title == ""
        assert news.subtitle == ""
        assert news.link == ""
        assert news.country_name == ""
        assert news.date is None
        assert news.author == ""


class TestNewsPage:
    def test_defaults(self):
        page = NewsPage()
        assert page.news == []
        assert page.has_next_page is False

    def test_creation(self):
        page = NewsPage(news=[News(id=1, title="Test")], has_next_page=True)
        assert len(page.news) == 1
        assert page.news[0].id == 1
        assert page.has_next_page is True
