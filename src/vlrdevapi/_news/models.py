from datetime import datetime as datetime_

from pydantic import BaseModel, ConfigDict, Field


class News(BaseModel): 
    model_config = ConfigDict(
        json_schema_extra={"description": "A news item from vlr.gg."}
    )

    id: int = Field(default=0, description="Unique identifier for the news item")
    title: str = Field(default="", description="Title of the news item")
    subtitle: str = Field(default="", description="Subtitle of the news item")
    link: str = Field(default="", description="Link to the news item")
    country_name: str = Field(default="", description="Country associated with the news item")
    date: datetime_ | None = Field(default=None, description="Date of the news item")
    author: str = Field(default="", description="Author of the news item")


class NewsPage(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A page of news items from vlr.gg."}
    )

    news: list[News] = Field(default_factory=list, description="List of news items")
    has_next_page: bool = Field(default=False, description="Whether there is a next page of results")
    page_number: int = Field(default=0, description="Current page number")