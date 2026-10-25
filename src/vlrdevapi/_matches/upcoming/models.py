
from datetime import datetime as datetime_
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class TeamInUpcomingMatch(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A team in an upcoming match entry."},
    )

    id: int = Field(default=0, description="Unique team identifier on vlr.gg")
    name: str = Field(default="", description="Full team name (e.g. 'NRG', 'FNATIC')")
    tag: str = Field(default="", description="Short team tag (e.g. 'NRG', 'FNC')")
    country_name: str = Field(
        default="", description="Full country name (e.g. 'United States')",
    )


class UpcomingMatchEntry(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "An upcoming match from vlr.gg."},
    )

    match_id: int = Field(default=0, description="Unique match identifier on vlr.gg")
    url: str = Field(default="", description="Relative URL to the match page")
    event: str = Field(default="", description="Event/tournament name")
    stage: str = Field(
        default="",
        description="Stage within the event (e.g. 'Playoffs', 'Swiss Stage')",
    )
    team1: TeamInUpcomingMatch | None = Field(default=None, description="First team")
    team2: TeamInUpcomingMatch | None = Field(default=None, description="Second team")
    status: str = Field(
        default="", description="Match status (e.g. 'upcoming', 'live')",
    )
    eta: str = Field(default="", description="Time until match starts (e.g. '1h 46m')")
    datetime: datetime_ | None = Field(
        default=None, description="Match datetime in UTC",
    )


class UpcomingMatchesPage(ExportableModel):
    model_config = ConfigDict(
        json_schema_extra={"description": "A page of upcoming matches from vlr.gg."},
    )

    matches: list[UpcomingMatchEntry] = Field(
        default_factory=list, description="List of upcoming match entries",
    )
    has_next_page: bool = Field(
        default=False, description="Whether there is a next page of results",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten upcoming matches into tabular records (1 row per match)."""
        records: list[dict[str, Any]] = []
        for m in self.matches:
            url = m.url
            if url and url.startswith("/"):
                url = f"https://www.vlr.gg{url}"
            elif not url and m.match_id:
                url = f"https://www.vlr.gg/{m.match_id}"

            t1_name = m.team1.name if (m.team1 and m.team1.name) else "TBD"
            t1_id = m.team1.id if (m.team1 and m.team1.id) else None
            t1_tag = (m.team1.tag if (m.team1 and m.team1.tag) else None) or ("TBD" if t1_name == "TBD" else None)
            t1_country = (m.team1.country_name if (m.team1 and m.team1.country_name) else None)

            t2_name = m.team2.name if (m.team2 and m.team2.name) else "TBD"
            t2_id = m.team2.id if (m.team2 and m.team2.id) else None
            t2_tag = (m.team2.tag if (m.team2 and m.team2.tag) else None) or ("TBD" if t2_name == "TBD" else None)
            t2_country = (m.team2.country_name if (m.team2 and m.team2.country_name) else None)

            records.append({
                "match_id": m.match_id,
                "event": m.event,
                "stage": m.stage,
                "eta": m.eta,
                "datetime": m.datetime.isoformat() if m.datetime else None,
                "team1_id": t1_id,
                "team1_name": t1_name,
                "team1_tag": t1_tag,
                "team1_country": t1_country,
                "team2_id": t2_id,
                "team2_name": t2_name,
                "team2_tag": t2_tag,
                "team2_country": t2_country,
                "url": url,
            })
        return records
