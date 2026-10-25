from datetime import datetime as datetime_
from typing import Any

from pydantic import ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class NewsArticle(ExportableModel):
    """A full news article from vlr.gg.

    Attributes:
        id: Unique identifier for the news article.
        title: Title of the news article.
        author: Author of the news article.
        date: Publication date as a timezone-aware UTC datetime.
        event_name: Event the article is associated with.
        event_link: Link to the associated event page.
        content: Full body text of the article as plain text.
        content_md: Full body of the article converted to Markdown, with
            headings, nested lists, tables, links, verbatim code, emphasis,
            and Twitch clip embeds preserved.
    """

    model_config = ConfigDict(
        json_schema_extra={"description": "A full news article from vlr.gg."}
    )

    id: int = Field(default=0, description="Unique identifier for the news article")
    title: str = Field(default="", description="Title of the news article")
    author: str = Field(default="", description="Author of the news article")
    date: datetime_ | None = Field(
        default=None, description="Publication date as a timezone-aware UTC datetime"
    )
    event_name: str = Field(
        default="", description="Event the article is associated with"
    )
    event_link: str = Field(default="", description="Link to the associated event page")
    content: str = Field(
        default="", description="Full text content of the news article"
    )
    content_md: str = Field(
        default="", description="Full content of the news article converted to Markdown"
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten article metadata and content into tabular records."""
        ev_link = self.event_link
        if ev_link and ev_link.startswith("/"):
            ev_link = f"https://www.vlr.gg{ev_link}"

        return [{
            "id": self.id,
            "title": self.title,
            "author": self.author or None,
            "date": self.date.isoformat() if self.date else None,
            "event_name": self.event_name or None,
            "event_link": ev_link or None,
            "url": f"https://www.vlr.gg/{self.id}",
            "char_count": len(self.content),
            "content": self.content,
            "content_md": self.content_md,
        }]
