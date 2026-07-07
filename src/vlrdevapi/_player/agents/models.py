from pydantic import BaseModel, ConfigDict, Field


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
    fkpr: float | None = Field(default=None, description="First Kills Per Round")
    fdpr: float | None = Field(default=None, description="First Deaths Per Round")
    kills: int | None = Field(default=None, description="Total kills")
    deaths: int | None = Field(default=None, description="Total deaths")
    assists: int | None = Field(default=None, description="Total assists")
    first_kills: int | None = Field(default=None, description="First bloods")
    first_deaths: int | None = Field(default=None, description="First deaths")


class AgentStatsPage(BaseModel):
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
