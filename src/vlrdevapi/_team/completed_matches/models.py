
from datetime import datetime as datetime_
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class OpponentInCompletedMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Opponent team in a completed match."},
    )

    id: int = Field(default=0, description="Opponent team ID")
    name: str = Field(default="", description="Opponent team name")
    tag: str = Field(default="", description="Opponent team tag")


class TeamCompletedMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A completed match for a specific team."},
    )

    match_id: int = Field(default=0, description="Match ID")
    url: str = Field(default="", description="Match URL")
    event: str = Field(default="", description="Event name")
    stage: str = Field(
        default="",
        description="Stage within the event (e.g. 'Playoffs', 'Group Stage')",
    )
    bracket: str = Field(
        default="",
        description="Bracket/round within the stage (e.g. 'LBF', 'Ro16')",
    )
    opponent: OpponentInCompletedMatch | None = Field(
        default=None, description="Opponent team",
    )
    team_score: int = Field(default=0, description="This team's score")
    opponent_score: int = Field(default=0, description="Opponent's score")
    is_win: bool = Field(default=False, description="Whether this team won")
    datetime: datetime_ | None = Field(default=None, description="Match datetime (UTC)")


class TeamCompletedMatches(ExportableModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "Collection of completed matches for a team."},
    )

    team_id: int = Field(default=0, description="Team ID")
    matches: list[TeamCompletedMatchEntry] = Field(
        default_factory=list, description="Completed matches",
    )
    has_next_page: bool = Field(
        default=False,
        description="Whether more completed matches exist beyond the returned results",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten completed matches into tabular records (1 row per match)."""
        records: list[dict[str, Any]] = []
        for m in self.matches:
            url = m.url
            if url and url.startswith("/"):
                url = f"https://www.vlr.gg{url}"
            elif not url and m.match_id:
                url = f"https://www.vlr.gg/{m.match_id}"

            opp_name = m.opponent.name if (m.opponent and m.opponent.name) else "TBD"
            opp_id = m.opponent.id if (m.opponent and m.opponent.id) else None
            opp_tag = m.opponent.tag if m.opponent else ""

            records.append({
                "team_id": self.team_id,
                "match_id": m.match_id,
                "event": m.event,
                "stage": m.stage,
                "bracket": m.bracket,
                "opponent_id": opp_id,
                "opponent_name": opp_name,
                "opponent_tag": opp_tag,
                "team_score": m.team_score,
                "opponent_score": m.opponent_score,
                "is_win": m.is_win,
                "datetime": m.datetime.isoformat() if m.datetime else None,
                "url": url,
            })
        return records
