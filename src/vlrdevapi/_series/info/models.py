

from datetime import datetime as _datetime

from pydantic import BaseModel, ConfigDict, Field


class SeriesTeam(BaseModel):
    """A team in a series/match on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "A team in a series/match on vlr.gg."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name (e.g. 'NRG', 'FNATIC')")
    tag: str = Field(default="", description="Short team tag (e.g. 'NRG', 'FNC')")
    logo_url: str = Field(default="", description="URL to the team logo image")


class MapVeto(BaseModel):
    """A single map veto/pick/decider entry in a series."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A single map veto/pick/decider entry in a series.",
        },
    )

    map_name: str = Field(default="", description="Map name (e.g. 'Corrode', 'Lotus')")
    veto_type: str = Field(default="", description="Veto type: 'ban', 'pick', or 'decider'")
    team: str = Field(
        default="", description="Team that banned/picked; empty for decider",
    )


class SeriesGame(BaseModel):
    """A single game/map within a series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A single game/map within a series on vlr.gg.",
        },
    )

    game_id: int = Field(
        default=0, description="Unique game identifier on vlr.gg (data-game-id)",
    )
    order: int = Field(default=0, description="Map order in the series (1-indexed)")
    map_name: str = Field(default="", description="Map name (e.g. 'Split', 'Breeze')")
    picked_by: str = Field(
        default="",
        description="Team tag that picked this map; empty for decider/not picked",
    )
    played: bool = Field(default=True, description="Whether the map was played")
    team1_score: int | None = Field(default=None, description="First team's score on this map")
    team2_score: int | None = Field(default=None, description="Second team's score on this map")
    team1_defense_rounds: int | None = Field(
        default=None, description="First team's rounds won on defense (CT side)",
    )
    team1_attack_rounds: int | None = Field(
        default=None, description="First team's rounds won on attack (T side)",
    )
    team2_attack_rounds: int | None = Field(
        default=None, description="Second team's rounds won on attack (T side)",
    )
    team2_defense_rounds: int | None = Field(
        default=None, description="Second team's rounds won on defense (CT side)",
    )
    team1_overtime_rounds: int | None = Field(
        default=None, description="First team's rounds won in overtime",
    )
    team2_overtime_rounds: int | None = Field(
        default=None, description="Second team's rounds won in overtime",
    )
    duration_seconds: int | None = Field(
        default=None, description="Match duration in seconds",
    )


class SeriesInfo(BaseModel):
    """Overview information for a match/series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Overview information for a match/series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    status: str = Field(
        default="", description="Match status: 'completed', 'live', or 'upcoming'",
    )
    team1: SeriesTeam = Field(default_factory=SeriesTeam, description="First team")
    team2: SeriesTeam = Field(default_factory=SeriesTeam, description="Second team")
    score1: int = Field(default=0, description="First team's series score")
    score2: int = Field(default=0, description="Second team's series score")
    best_of: int = Field(default=0, description="Best of N (e.g. 1, 3, 5)")
    event_id: int = Field(default=0, description="Unique event identifier on vlr.gg")
    event_name: str = Field(
        default="", description="Event name (e.g. 'Valorant Champions 2025')",
    )
    stage: str = Field(default="", description="Stage within event (e.g. 'Playoffs')")
    bracket: str = Field(default="", description="Bracket/round (e.g. 'Grand Final')")
    datetime: _datetime | None = Field(
        default=None, description="Combined UTC datetime of the match",
    )
    patch: str = Field(
        default="",
        description="Patch version only (e.g. '11.05', NOT 'Patch 11.05')",
    )
    veto: list[MapVeto] = Field(default_factory=list, description="Map veto/pick/ban info")
    games: list[SeriesGame] = Field(default_factory=list, description="Games/maps in the series")
