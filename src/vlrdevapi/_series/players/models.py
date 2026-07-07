
from pydantic import BaseModel, ConfigDict, Field


class SideStats(BaseModel):
    """Stats for one side: overall, attack, or defend."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Stats for one side: overall, attack, or defend.",
        },
    )

    rating: float | None = Field(default=None, description="VLR rating (normalised performance metric)")
    acs: float | None = Field(default=None, description="Average Combat Score")
    kills: int | None = Field(default=None, description="Total kills")
    deaths: int | None = Field(default=None, description="Total deaths")
    assists: int | None = Field(default=None, description="Total assists")
    kd_diff: int | None = Field(default=None, description="Kill/death differential")
    kast: float | None = Field(default=None, description="KAST percentage (kill, assist, survive, trade)")
    adr: float | None = Field(default=None, description="Average Damage per Round")
    hs_percent: float | None = Field(default=None, description="Headshot percentage")
    first_kills: int | None = Field(default=None, description="Total first kills")
    first_deaths: int | None = Field(default=None, description="Total first deaths")
    fk_fd_diff: int | None = Field(default=None, description="First kill/first death differential")


class PlayerStats(BaseModel):
    """Three-way stats: overall, attack, and defend."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Three-way stats: overall + attack + defend."},
    )

    overall: SideStats = Field(default_factory=SideStats, description="Stats across all sides (attack + defend combined)")
    attack: SideStats = Field(default_factory=SideStats, description="Stats on the attack side only")
    defend: SideStats = Field(default_factory=SideStats, description="Stats on the defense side only")


class PlayerGameStats(BaseModel):
    """Per-player stats within a specific game/overview."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Per-player stats within a specific game/overview.",
        },
    )

    player_id: int = Field(default=0, description="Unique player identifier on vlr.gg")
    name: str = Field(default="", description="Player in-game name")
    country_code: str = Field(default="", description="Two-letter country code (e.g., 'US')")
    country: str = Field(default="", description="Full country name")
    team_short: str = Field(default="", description="Team abbreviation/tag")
    agents: list[str] = Field(default_factory=list, description="Agents played by this player in the game")
    stats: PlayerStats = Field(default_factory=PlayerStats, description="Three-way stats (overall, attack, defend)")


class TeamPlayers(BaseModel):
    """All players for one team in a game."""

    model_config = ConfigDict(
        json_schema_extra={"description": "All players for one team in a game."},
    )

    team_id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    team_name: str = Field(default="", description="Full team name")
    team_short: str = Field(default="", description="Team abbreviation/tag")
    players: list[PlayerGameStats] = Field(default_factory=list, description="List of players with their per-game stats")


class PlayersStats(BaseModel):
    """Player statistics for a series game on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Player statistics for a series game on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    game_id: str = Field(default="all", description="Game/map identifier ('all' for combined, or numeric ID)")
    map_name: str = Field(default="", description="Map name (e.g., 'Haven', 'Bind', 'Ascent')")
    team1: TeamPlayers = Field(default_factory=TeamPlayers, description="Team 1 player stats")
    team2: TeamPlayers = Field(default_factory=TeamPlayers, description="Team 2 player stats")
