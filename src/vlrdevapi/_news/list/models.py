from datetime import datetime as datetime_
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class News(BaseModel):
    """A single news item from the vlr.gg news listing.

    Attributes:
        id: Unique identifier for the news item.
        title: Title of the news item.
        subtitle: Short subtitle or summary.
        link: Relative URL to the article page.
        country_name: Country associated with the item, derived from the
            flag icon shown next to it.
        date: Publication date as a timezone-aware UTC datetime.
        author: Author of the news item.
    """

    model_config = ConfigDict(
        json_schema_extra={"description": "A news item from vlr.gg."}
    )

    id: int = Field(default=0, description="Unique identifier for the news item")
    title: str = Field(default="", description="Title of the news item")
    subtitle: str = Field(default="", description="Subtitle of the news item")
    link: str = Field(default="", description="Link to the news item")
    country_name: str = Field(
        default="", description="Country associated with the news item"
    )
    date: datetime_ | None = Field(
        default=None,
        description="Publication date as a timezone-aware UTC datetime",
    )
    author: str = Field(default="", description="Author of the news item")


class NewsPage(ExportableModel):
    """A single page of news items from the vlr.gg news listing.

    Attributes:
        news: The news items shown on this page.
        has_next_page: Whether more pages of results exist after this one.
        page_number: The current page number (1-indexed).
    """

    model_config = ConfigDict(
        json_schema_extra={"description": "A page of news items from vlr.gg."}
    )

    news: list[News] = Field(default_factory=list, description="List of news items")
    has_next_page: bool = Field(
        default=False, description="Whether there is a next page of results"
    )
    page_number: int = Field(default=0, description="Current page number")

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten news articles into tabular records (1 row per article)."""
        records: list[dict[str, Any]] = []
        for n in self.news:
            url = n.link
            if url and url.startswith("/"):
                url = f"https://www.vlr.gg{url}"
            elif not url and n.id:
                url = f"https://www.vlr.gg/{n.id}"

            records.append({
                "id": n.id,
                "title": n.title,
                "subtitle": n.subtitle,
                "author": n.author,
                "date": n.date.isoformat() if n.date else None,
                "country_name": n.country_name,
                "url": url,
            })
        return records
