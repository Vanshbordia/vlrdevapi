from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class TeamPlayer(BaseModel):
    """Player information for a team at an event."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Player information for a team at an event."},
    )

    id: int = Field(
        default=0,
        description="Player identifier from vlr.gg (e.g., 1311)",
    )
    name: str = Field(
        default="",
        description="Player in-game name (e.g., 'Melser')",
    )


class Team(BaseModel):
    """Team information for an event from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Team information for an event from vlr.gg."},
    )

    name: str = Field(
        default="",
        description="Team name (e.g., 'NRG')",
    )
    id: int = Field(
        default=0,
        description="Team identifier from vlr.gg (e.g., 1034)",
    )
    note: str | None = Field(
        default=None,
        description="Optional note (e.g., 'Partner Team')",
    )
    players: list[TeamPlayer] = Field(
        default_factory=list,
        description="List of players on the team (name and id). Always present; empty when roster data is unavailable.",
    )


class EventStageTeams(BaseModel):
    """Teams grouped by event stage from vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Teams grouped by event stage from vlr.gg."},
    )

    stage_path: str = Field(
        default="",
        description="Stage path (e.g., 'group-stage')",
    )
    stage_name: str = Field(
        default="",
        description="Stage name (e.g., 'Group Stage')",
    )
    teams: list[Team] = Field(
        default_factory=list,
        description="List of teams in this stage",
    )

class EventTeams(ExportableModel):
    """Wrapper for teams grouped by stage."""

    model_config = ConfigDict(
        json_schema_extra={"description": "Wrapper for event teams."},
    )
    stages: list[EventStageTeams] = Field(
        default_factory=list,
        description="List of stages containing teams",
    )

    def to_records(self, by_player: bool = False, **kwargs: Any) -> list[dict[str, Any]]:
        """Convert event teams to tabular records.

        Args:
            by_player: If True, returns 1 row per player on each team.
                       If False (default), returns 1 row per team with players list.
        """
        records: list[dict[str, Any]] = []
        for stage in self.stages:
            for team in stage.teams:
                team_url = f"https://www.vlr.gg/team/{team.id}" if team.id else None
                if by_player:
                    for p in team.players:
                        records.append({
                            "stage_path": stage.stage_path,
                            "stage_name": stage.stage_name,
                            "team_id": team.id or None,
                            "team_name": team.name or "TBD",
                            "note": team.note or None,
                            "player_id": p.id or None,
                            "player_name": p.name,
                            "player_url": f"https://www.vlr.gg/player/{p.id}" if p.id else None,
                            "team_url": team_url,
                        })
                else:
                    player_names = [p.name for p in team.players] if team.players else []
                    records.append({
                        "stage_path": stage.stage_path,
                        "stage_name": stage.stage_name,
                        "team_id": team.id or None,
                        "team_name": team.name or "TBD",
                        "note": team.note or None,
                        "player_count": len(team.players),
                        "players": player_names,
                        "url": team_url,
                    })
        return records

    def __len__(self) -> int:
        return len(self.stages)

    def __iter__(self):  # type: ignore[override]
        return iter(self.stages)

    def __getitem__(self, index):
        return self.stages[index]