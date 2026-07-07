
from pydantic import BaseModel, ConfigDict, Field


class KillEntry(BaseModel):
    """A single killer-victim pair with kill/death counts."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A single killer-victim pair with kill/death counts.",
        },
    )

    killer: str = Field(default="", description="Killer player name")
    killer_id: int = Field(default=0, description="Killer player ID on vlr.gg")
    killer_team: str = Field(default="", description="Killer team abbreviation")
    victim: str = Field(default="", description="Victim player name")
    victim_id: int = Field(default=0, description="Victim player ID on vlr.gg")
    victim_team: str = Field(default="", description="Victim team abbreviation")
    kills: int | None = Field(default=None, description="Total kills by the killer (None if data unavailable)")
    deaths: int | None = Field(default=None, description="Total deaths of the killer (None if data unavailable)")
    diff: int | None = Field(default=None, description="Kill/death differential (None if data unavailable)")


class KillMatrix(BaseModel):
    """A kill matrix as flat entries for all kills, first kills, or op kills."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A kill matrix (all kills, first kills, or op kills) as flat entries.",
        },
    )

    entries: list[KillEntry] = Field(default_factory=list, description="Kill entries comprising the kill matrix")

    def lookup(self, killer: str, victim: str) -> KillEntry | None:
        """Look up a kill entry by killer and victim names.

        Args:
            killer: The killer player name.
            victim: The victim player name.

        Returns:
            KillEntry | None: The matching entry, or None.

        """
        for e in self.entries:
            if e.killer == killer and e.victim == victim:
                return e
        return None

    def by_killer(self, name: str) -> list[KillEntry]:
        """Return all entries where the given player is the killer.

        Args:
            name: The player name to filter by.

        Returns:
            list[KillEntry]: Matching kill entries.

        """
        return [e for e in self.entries if e.killer == name]

    def by_victim(self, name: str) -> list[KillEntry]:
        """Return all entries where the given player is the victim.

        Args:
            name: The player name to filter by.

        Returns:
            list[KillEntry]: Matching kill entries.

        """
        return [e for e in self.entries if e.victim == name]

    def by_team(self, team: str) -> list[KillEntry]:
        """Return all entries where either player belongs to the given team.

        Args:
            team: The team abbreviation to filter by.

        Returns:
            list[KillEntry]: Matching kill entries.

        """
        return [
            e for e in self.entries if e.killer_team == team or e.victim_team == team
        ]

    def killers(self) -> list[str]:
        """Return an ordered list of unique killer names.

        Returns:
            list[str]: Unique killer names in order of first appearance.

        """
        seen: list[str] = []
        for e in self.entries:
            if e.killer not in seen:
                seen.append(e.killer)
        return seen

    def victims(self) -> list[str]:
        """Return an ordered list of unique victim names.

        Returns:
            list[str]: Unique victim names in order of first appearance.

        """
        seen: list[str] = []
        for e in self.entries:
            if e.victim not in seen:
                seen.append(e.victim)
        return seen


class NotableVictim(BaseModel):
    """A victim in a notable round with name and player ID."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A victim in a notable round with name and player ID.",
        },
    )

    name: str = Field(default="", description="Victim player name")
    player_id: int | None = Field(default=None, description="Victim player ID on vlr.gg")


class AdvStatsNotableRound(BaseModel):
    """A notable round detail for a multi-kill or clutch."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A notable round detail for a multi-kill or clutch.",
        },
    )

    round_number: int | None = Field(default=None, description="Round number in the game")
    victims: list[NotableVictim] = Field(default_factory=list, description="List of victims in this notable round")


class AdvStatsEntry(BaseModel):
    """Advanced stats entry for a player in a game."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Advanced stats entry for a player in a game.",
        },
    )

    player_id: int = Field(default=0, description="Unique player identifier on vlr.gg")
    name: str = Field(default="", description="Player in-game name")
    team_short: str = Field(default="", description="Team abbreviation/tag")
    agent: str = Field(default="", description="Agent played in this game")
    two_k: int | None = Field(default=None, description="Number of rounds with exactly 2 kills")
    three_k: int | None = Field(default=None, description="Number of rounds with exactly 3 kills")
    four_k: int | None = Field(default=None, description="Number of rounds with exactly 4 kills")
    five_k: int | None = Field(default=None, description="Number of rounds with exactly 5 kills")
    one_v1: int | None = Field(default=None, description="Number of 1v1 clutches won")
    one_v2: int | None = Field(default=None, description="Number of 1v2 clutches won")
    one_v3: int | None = Field(default=None, description="Number of 1v3 clutches won")
    one_v4: int | None = Field(default=None, description="Number of 1v4 clutches won")
    one_v5: int | None = Field(default=None, description="Number of 1v5 clutches won")
    econ: int | None = Field(default=None, description="Econ rating")
    pl: int | None = Field(default=None, description="Plant (spike plants)")
    de: int | None = Field(default=None, description="Defuse (spike defuses)")
    two_k_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 2K rounds")
    three_k_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 3K rounds")
    four_k_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 4K rounds")
    five_k_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 5K rounds")
    one_v1_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 1v1 clutches")
    one_v2_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 1v2 clutches")
    one_v3_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 1v3 clutches")
    one_v4_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 1v4 clutches")
    one_v5_rounds: list[AdvStatsNotableRound] = Field(default_factory=list, description="Detailed round info for 1v5 clutches")


class PerformanceData(BaseModel):
    """Performance metrics for a game/map within a series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Performance metrics for a game/map within a series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    game_id: str = Field(default="all", description="Game/map identifier ('all' for combined, or numeric ID)")
    all_kills_matrix: KillMatrix = Field(
        default_factory=KillMatrix,
        description="All kills kill matrix.",
    )
    first_kills_matrix: KillMatrix = Field(
        default_factory=KillMatrix,
        description="First kills kill matrix.",
    )
    op_kills_matrix: KillMatrix = Field(
        default_factory=KillMatrix,
        description="Op kills kill matrix.",
    )
    adv_stats: list[AdvStatsEntry] = Field(
        default_factory=list,
        description="Advanced stats entries (2K, 3K, clutches, etc.).",
    )
