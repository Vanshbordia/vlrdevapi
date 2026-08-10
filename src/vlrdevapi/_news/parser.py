"""Parse upcoming news from vlr.gg/news HTML page"""

import logging
from datetime import date, tzinfo
from zoneinfo import ZoneInfo

import httpx
from selectolax.parser import HTMLParser, Node

from vlrdevapi._cache import LRUCache
from vlrdevapi._news.common import check_pagination
from vlrdevapi._news.models import News, NewsPage


def _():
    pass


def parse_news_page():
    pass


def _parse_news_item():
    pass