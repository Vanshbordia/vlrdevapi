import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


class AgentStats(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Per-agent statistics for a player on vlr.gg.",
        },
    )

    agent: str = Field(default="", description="Agent name (e.g. 'neon')")
    use: str = Field(default="", description="Usage string (e.g. '(12) 46%')")
    rounds: int | None = Field(default=None, description="Rounds played")
    rating: float | None = Field(default=None, description="Rating 2.0")
    acs: float | None = Field(default=None, description="Average Combat Score")
    kd: float | None = Field(default=None, description="Kill/Death ratio")
    adr: float | None = Field(default=None, description="Average Damage per Round")
    kast: str = Field(default="", description="Kill, Assist, Survive, Trade %")
    kpr: float | None = Field(default=None, description="Kills Per Round")
    apr: float | None = Field(default=None, description="Assists Per Round")
    kills: int | None = Field(default=None, description="Total kills")
    deaths: int | None = Field(default=None, description="Total deaths")
    assists: int | None = Field(default=None, description="Total assists")
    first_kills: int | None = Field(default=None, description="First bloods")
    first_deaths: int | None = Field(default=None, description="First deaths")


class AgentStatsPage(ExportableModel):
    model_config = ConfigDict(
        json_schema_extra={
            "description": "Per-agent statistics for a player on vlr.gg, filtered by timespan.",
        },
    )

    timespan: str = Field(
        default="all", description="Timespan used for the query (30d, 60d, 90d, all)",
    )
    agents: list[AgentStats] = Field(
        default_factory=list, description="List of per-agent statistic entries",
    )

    def to_records(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Flatten agent statistics into tabular records (1 row per agent)."""
        records: list[dict[str, Any]] = []
        for a in self.agents:
            use_count: int | None = None
            use_pct: float | None = None
            if a.use:
                m = re.search(r"\((\d+)\)\s*(\d+(?:\.\d+)?)\s*%", a.use)
                if m:
                    use_count = int(m.group(1))
                    use_pct = float(m.group(2))

            kast_num: float | None = None
            if a.kast:
                try:
                    kast_num = float(a.kast.replace("%", "").strip())
                except ValueError:
                    kast_num = None

            records.append({
                "timespan": self.timespan,
                "agent": a.agent,
                "use": a.use or None,
                "use_count": use_count,
                "use_percent": use_pct,
                "rounds": a.rounds,
                "rating": a.rating,
                "acs": a.acs,
                "kd": a.kd,
                "adr": a.adr,
                "kast": kast_num,
                "kpr": a.kpr,
                "apr": a.apr,
                "kills": a.kills,
                "deaths": a.deaths,
                "assists": a.assists,
                "first_kills": a.first_kills,
                "first_deaths": a.first_deaths,
            })
        return records
