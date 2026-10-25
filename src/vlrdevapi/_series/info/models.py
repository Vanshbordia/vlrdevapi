

from datetime import date as _date
from datetime import datetime as _datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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


class ForfeitInfo(BaseModel):
    """Forfeit/walkover information for a match."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Forfeit/walkover information for a match.",
        },
    )

    forfeited: bool = Field(default=False, description="Whether the match was forfeited")
    team: str | None = Field(
        default=None, description="Full name of the team that forfeited",
    )
    team_id: int | None = Field(
        default=None, description="vlr.gg team ID of the forfeiting team",
    )
    reason: str | None = Field(
        default=None, description="Forfeit explanation from match notes",
    )


class SeriesHeadToHeadMatch(BaseModel):
    """A previous match between the two teams in a series."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A previous match between the two teams in a series.",
        },
    )

    series_id: int = Field(
        default=0, description="Unique identifier of the previous series on vlr.gg",
    )
    url: str = Field(
        default="", description="Full URL to the previous series on vlr.gg",
    )
    event_name: str = Field(default="", description="Event name")
    stage: str = Field(
        default="", description="Stage or round label (e.g. 'UBF', 'Group Stage')",
    )
    date: _date | None = Field(
        default=None, description="Date the previous match was played",
    )
    team1_name: str = Field(
        default="", description="First team name, in the head-to-head header order",
    )
    team1_score: int = Field(default=0, description="First team's series score")
    team2_name: str = Field(
        default="", description="Second team name, in the head-to-head header order",
    )
    team2_score: int = Field(default=0, description="Second team's series score")
    winner: Literal["team1", "team2", ""] = Field(
        default="",
        description="Which side won, relative to the head-to-head team order",
    )


class SeriesInfo(ExportableModel):
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
    forfeit: ForfeitInfo = Field(
        default_factory=ForfeitInfo,
        description="Forfeit/walkover information if the match was forfeited",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Non-veto match notes (e.g. technical pauses, lobby remakes)",
    )
    head_to_head: list[SeriesHeadToHeadMatch] = Field(
        default_factory=list,
        description="Previous matches between the two teams",
    )

    def to_records(self, view: str = "games", **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten series overview into tabular records.

        Args:
            view: Either 'games' (default: 1 row per map/game in the series) or
                'summary' (single row with overall series metadata and final score).
            **kwargs: Extra parameters (ignored).
        """
        t1_name = self.team1.name or "TBD"
        t2_name = self.team2.name or "TBD"
        dt_str = self.datetime.isoformat() if self.datetime else None
        url = f"https://www.vlr.gg/{self.series_id}"

        if view == "summary" or not self.games:
            return [{
                "series_id": self.series_id,
                "status": self.status,
                "event_id": self.event_id,
                "event_name": self.event_name,
                "stage": self.stage,
                "bracket": self.bracket,
                "best_of": self.best_of,
                "patch": self.patch,
                "datetime": dt_str,
                "team1_id": self.team1.id or None,
                "team1_name": t1_name,
                "team1_tag": self.team1.tag,
                "score1": self.score1,
                "team2_id": self.team2.id or None,
                "team2_name": t2_name,
                "team2_tag": self.team2.tag,
                "score2": self.score2,
                "url": url,
            }]

        records: list[dict[str, Any]] = []
        for g in self.games:
            records.append({
                "series_id": self.series_id,
                "game_id": g.game_id,
                "order": g.order,
                "map_name": g.map_name,
                "picked_by": g.picked_by,
                "played": g.played,
                "team1_name": t1_name,
                "team1_score": g.team1_score,
                "team2_name": t2_name,
                "team2_score": g.team2_score,
                "event_name": self.event_name,
                "stage": self.stage,
                "bracket": self.bracket,
                "patch": self.patch,
                "datetime": dt_str,
                "url": url,
            })
        return records
