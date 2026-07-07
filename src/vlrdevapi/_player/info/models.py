from pydantic import BaseModel, ConfigDict, Field


class PlayerInfo(BaseModel):
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
