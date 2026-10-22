"""Data models for the series replay (kill-feed timeline) module."""

from enum import Enum, StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ArmorType(StrEnum):
    """Armor purchased or equipped by a player for a round."""

    NO_ARMOR = "No armor"
    """Player has no armor equipped (0 HP shield)."""
    LIGHT = "Light armor"
    """Light shields (25 HP shield, 400 creds)."""
    HEAVY = "Heavy armor"
    """Heavy shields (50 HP shield, 1000 creds)."""
    REGEN = "Regen Shield"
    """Regenerative shield (regenerates shield health)."""


class PlayerRoundLoadout(BaseModel):
    """Buy-phase loadout and economy state for a single player in a round."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Buy-phase loadout for one player in a replay round.",
        },
        use_enum_values=True,
    )

    player_id: int = Field(
        default=0,
        description="Unique player ID on vlr.gg (0 when not matched from overview)",
    )
    name: str = Field(default="", description="Player name")
    team: str = Field(default="", description="Team tag or name")
    agent: str = Field(default="", description="Agent name (e.g. 'Sage', 'Neon')")
    side: str = Field(
        default="",
        description="Side the player played in this round: 'Attack' or 'Defense'",
    )
    weapon: str = Field(
        default="",
        description="Equipped weapon at round start (e.g. 'Ghost', 'Vandal', 'Operator')",
    )
    armor: ArmorType = Field(
        default=ArmorType.NO_ARMOR,
        description="Equipped armor ('No armor', 'Light armor', 'Heavy armor', 'Regen Shield')",
    )
    credits_left: int = Field(
        default=0,
        description="Credits remaining after the buy phase",
    )
    spent: int = Field(
        default=0,
        description="Credits spent in the buy phase",
    )


class ReplayEventType(Enum):
    """Type of an event in a round's replay timeline.

    ``kill``, ``plant``, and ``defuse`` are logged as kill-feed rows on
    vlr.gg; ``boom`` (spike detonation) and ``resurrect`` (a player
    returning to life) are derived by vlrdevapi because vlr.gg logs
    neither as feed rows.
    """

    KILL = "kill"
    """Player eliminated another player."""
    PLANT = "plant"
    """Spike planted on a site."""
    DEFUSE = "defuse"
    """Spike defused."""
    BOOM = "boom"
    """Spike detonation (derived; vlr.gg does not log it as a feed row)."""
    RESURRECT = "resurrect"
    """Player returned to life (derived; vlr.gg does not log it as a feed row)."""

    @property
    def full_name(self) -> str:
        """Return the human-readable name for this event type."""
        return {
            "kill": "Kill",
            "plant": "Planted",
            "defuse": "Defused",
            "boom": "Spike detonated",
            "resurrect": "Resurrected",
        }.get(self.value, self.value)


class ReplayActor(BaseModel):
    """A player identified in a replay event (killer, planter, defuser, revived)."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A player identified in a replay event on vlr.gg.",
        },
    )

    player_id: int = Field(
        default=0,
        description="Unique player ID on vlr.gg (matched within the player's team from the game overview tab; 0 when the player cannot be matched)",
    )
    name: str = Field(default="", description="Player name")
    agent: str = Field(
        default="",
        description="Agent key in lowercase as shown on vlr.gg (e.g. 'omen')",
    )
    team: str = Field(default="", description="Team name the player belongs to this round")
    side: str = Field(
        default="",
        description="Side the player was on this round: 'Attack' or 'Defense'",
    )


class ReplayPlayerRef(BaseModel):
    """Player roster entry for one replay round."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Player roster entry for one replay round on vlr.gg.",
        },
    )

    player_id: int = Field(
        default=0,
        description="Unique player ID on vlr.gg (matched within the player's team from the game overview tab; 0 when the player cannot be matched)",
    )
    name: str = Field(default="", description="Player name")
    agent: str = Field(
        default="",
        description="Agent key in lowercase as shown on vlr.gg (e.g. 'omen')",
    )
    team: str = Field(default="", description="Team name the player belongs to this round")
    side: str = Field(
        default="",
        description="Side the player was on this round: 'Attack' or 'Defense'",
    )


class ReplayAlivePlayer(BaseModel):
    """One player's position state in a per-event alive snapshot."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Player position state in a replay alive snapshot on vlr.gg.",
        },
    )

    player_id: int = Field(
        default=0,
        description="Unique player ID on vlr.gg (matched within the player's team from the game overview tab; 0 when the player cannot be matched)",
    )
    name: str = Field(default="", description="Player name")
    agent: str = Field(
        default="",
        description="Agent key in lowercase as shown on vlr.gg (e.g. 'omen')",
    )
    team: str = Field(default="", description="Team name the player belongs to this round")
    side: str = Field(
        default="",
        description="Side the player was on this round: 'Attack' or 'Defense'",
    )
    x: float = Field(default=0.0, description="Map coordinate on the 1024x1024 minimap grid")
    y: float = Field(default=0.0, description="Map coordinate on the 1024x1024 minimap grid")
    view_angle: int = Field(
        default=0,
        description="Facing direction in minimap degrees (0 points to +x, rotates clockwise)",
    )


class ReplayEvent(BaseModel):
    """A single event in a round's kill-feed timeline.

    ``type`` is a ``ReplayEventType``. ``derived`` is ``True`` for the
    two event kinds vlr.gg does not log as feed rows (``boom`` and
    ``resurrect``).
    """

    model_config = ConfigDict(
        json_schema_extra={
            "description": "A single event in a round's kill-feed timeline on vlr.gg.",
        },
    )

    seq: int = Field(default=0, description="Event position within the round (0-based)")
    type: ReplayEventType = Field(
        default=ReplayEventType.KILL,
        description="Event type (ReplayEventType: KILL, PLANT, DEFUSE, BOOM, or RESURRECT)",
    )
    clock: str = Field(
        default="",
        description="Round clock at the event (M:SS); empty for the boom marker when vlr.gg reports no following event",
    )
    seconds: int | None = Field(
        default=None,
        description="Round clock at the event in seconds; None when no clock is reported (e.g. a round-ending boom marker after the last feed row)",
    )
    actor: ReplayActor | None = Field(
        default=None,
        description="Acting player (killer, planter, defuser, or revived player)",
    )
    victim: ReplayActor | None = Field(
        default=None,
        description="Killed player (kill events only)",
    )
    cause: str = Field(
        default="",
        description="Kill cause: the weapon or the ability/ult/spike name (kill events only)",
    )
    site: str = Field(
        default="",
        description="Spike site letter ('A', 'B', or 'C') for spike events; empty otherwise",
    )
    pos_x: float | None = Field(
        default=None,
        description="Event X coordinate on the 1024x1024 minimap grid (kills: victim position; plants/defuses: actor position)",
    )
    pos_y: float | None = Field(
        default=None,
        description="Event Y coordinate on the 1024x1024 minimap grid (kills: victim position; plants/defuses: actor position)",
    )
    from_x: float | None = Field(
        default=None,
        description="Killer X coordinate at the moment of the kill (kill events only)",
    )
    from_y: float | None = Field(
        default=None,
        description="Killer Y coordinate at the moment of the kill (kill events only)",
    )
    distance_units: float | None = Field(
        default=None,
        description="Euclidean killer-to-victim distance in minimap units (kill events only; no meters scale exists on vlr.gg)",
    )
    alive: list[ReplayAlivePlayer] = Field(
        default_factory=list,
        description="Alive players snapshot at this event with map coordinates and facing angles",
    )
    derived: bool = Field(
        default=False,
        description="Whether this event was derived ('boom'/'resurrect') rather than logged as a feed row on vlr.gg",
    )


class ReplayRound(BaseModel):
    """Full kill-feed replay timeline for one round of a game/map on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Kill-feed replay timeline for one round on vlr.gg.",
        },
    )

    round_number: int = Field(default=0, description="Round number in the game")
    attacking: str = Field(
        default="",
        description="Name of the team attacking (planting) in this round",
    )
    loadouts: list[PlayerRoundLoadout] = Field(
        default_factory=list,
        description="Buy-phase loadouts for all players in this round (equipped weapon, armor, and credits)",
    )
    players: list[ReplayPlayerRef] = Field(
        default_factory=list,
        description="The ten players with real player ID, agent, team, and side",
    )
    events: list[ReplayEvent] = Field(
        default_factory=list,
        description="Ordered kill-feed events, including derived 'boom' and 'resurrect' entries",
    )
    boom_at: int | None = Field(
        default=None,
        description="Raw vlr.gg detonation marker: the spike explodes between event ``boom_at - 1`` and event ``boom_at``",
    )

    def loadout_for(self, player: str | int) -> PlayerRoundLoadout | None:
        """Return the loadout for a player by name or player ID, or None.

        Args:
            player: Player name (case-insensitive) or integer player ID.

        Returns:
            PlayerRoundLoadout | None: The matching loadout, or None.

        """
        if isinstance(player, int):
            for ld in self.loadouts:
                if ld.player_id == player:
                    return ld
        else:
            key = str(player).casefold()
            for ld in self.loadouts:
                if ld.name.casefold() == key:
                    return ld
        return None


class ReplayData(BaseModel):
    """Kill-feed replay timeline for a game/map within a series on vlr.gg."""

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Kill-feed replay timeline for a game/map within a series on vlr.gg.",
        },
    )

    series_id: int = Field(default=0, description="Unique series identifier on vlr.gg")
    game_id: int = Field(default=0, description="Unique game identifier on vlr.gg")
    team1: str = Field(default="", description="Team 1 name from the round scoreboard band")
    team2: str = Field(default="", description="Team 2 name from the round scoreboard band")
    team1_id: int = Field(
        default=0,
        description="Team 1 ID on vlr.gg (matched from the game's overview tab header; 0 when not matched)",
    )
    team2_id: int = Field(
        default=0,
        description="Team 2 ID on vlr.gg (matched from the game's overview tab header; 0 when not matched)",
    )
    num_rounds: int = Field(default=0, description="Number of rounds with replay data")
    rounds: list[ReplayRound] = Field(
        default_factory=list,
        description="Replay rounds in play order",
    )

    def round(self, round_number: int) -> ReplayRound | None:
        """Return the timeline for one 1-based round number, or ``None``.

        Args:
            round_number: Round number within the game (e.g. ``9``).

        Returns:
            ReplayRound | None: The matching ``ReplayRound``, or ``None``
            when the round has no replay data.

        """
        for round_data in self.rounds:
            if round_data.round_number == round_number:
                return round_data
        return None
