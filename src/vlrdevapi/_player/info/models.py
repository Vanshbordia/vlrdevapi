from typing import Any

from pydantic import ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class PlayerInfo(ExportableModel):
    """Detailed information about a player on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Detailed information about a player on vlr.gg.",
        },
    )

    player_id: int = Field(default=0, description="Unique player identifier on vlr.gg")
    name: str = Field(default="", description="Player in-game name")
    real_name: str = Field(default="", description="Player's real name")
    img: str = Field(default="", description="URL to the player's profile image")
    x_link: str = Field(default="", description="Player's X (Twitter) profile URL")
    x_handle: str = Field(
        default="", description="Player's X (Twitter) handle (e.g. '@ethanarnold')",
    )
    twitch_link: str = Field(default="", description="Player's Twitch profile URL")
    twitch_handle: str = Field(
        default="", description="Player's Twitch handle (e.g. 'ethancs')",
    )
    country: str = Field(
        default="", description="Player's country of origin (e.g. 'UNITED STATES')",
    )
    country_code: str = Field(
        default="", description="Two-letter country code (e.g. 'us')",
    )
    aliases: list[str] = Field(
        default_factory=list, description="Player's known aliases / former names",
    )
    total_winnings: int | None = Field(
        default=None, description="Total prize money as a numeric value",
    )
    total_winnings_currency: str | None = Field(
        default=None, description="Currency symbol for total winnings (e.g. '$')",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten player info into a clean scalar tabular record."""
        return [{
            "player_id": self.player_id,
            "name": self.name,
            "real_name": self.real_name or None,
            "country": self.country or None,
            "country_code": self.country_code or None,
            "url": f"https://www.vlr.gg/player/{self.player_id}",
            "x_handle": self.x_handle or None,
            "x_link": self.x_link or None,
            "twitch_handle": self.twitch_handle or None,
            "twitch_link": self.twitch_link or None,
            "aliases": list(self.aliases) if self.aliases else [],
            "total_winnings": self.total_winnings,
            "total_winnings_currency": self.total_winnings_currency or None,
            "img": self.img or None,
        }]
