
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from vlrdevapi.commons.export import ExportableModel


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


class PlayersStats(ExportableModel):
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
    maps: list[Any] = Field(default_factory=list, description="Per-map player statistics when available")

    def to_records(
        self,
        side: str = "all_splits",
        include_maps: bool = True,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Flatten player statistics across both teams into tabular records.

        Args:
            side: Stats presentation format:
                - 'all_splits' / 'wide' (default): 1 row per player with complete
                  overall, attack, and defense stats side-by-side as dedicated columns.
                - 'overall': 1 row per player with overall combined stats only.
                - 'attack': 1 row per player with attack stats only.
                - 'defend': 1 row per player with defense stats only.
                - 'long' / 'split': 3 rows per player with a 'side' column.
            include_maps: Whether to include individual map rows along with the series summary.
            **kwargs: Extra parameters (ignored).
        """
        records: list[dict[str, Any]] = []

        target_games: list[PlayersStats] = []
        if include_maps and self.maps:
            target_games.extend(self.maps)
        target_games.append(self)

        for g in target_games:
            map_display = g.map_name or ("All Maps" if str(g.game_id).lower() == "all" else f"Map {g.game_id}")

            if side in ("long", "split", "all"):
                for team in (g.team1, g.team2):
                    t_name = team.team_name or "TBD"
                    t_tag = team.team_short or (t_name if t_name == "TBD" else None)
                    for p in team.players:
                        for s_name in ("overall", "attack", "defend"):
                            side_stat = getattr(p.stats, s_name, None)
                            rec: dict[str, Any] = {
                                "series_id": g.series_id or self.series_id,
                                "game_id": g.game_id,
                                "map_name": map_display,
                                "team_id": team.team_id or None,
                                "team_name": t_name,
                                "team_tag": t_tag,
                                "player_id": p.player_id,
                                "name": p.name,
                                "country_code": p.country_code or None,
                                "country": p.country or None,
                                "primary_agent": p.agents[0] if p.agents else None,
                                "agents": list(p.agents),
                                "side": s_name,
                                "url": f"https://www.vlr.gg/{self.series_id or g.series_id}",
                            }
                            if side_stat is not None:
                                rec.update({
                                    "rating": side_stat.rating,
                                    "acs": side_stat.acs,
                                    "kills": side_stat.kills,
                                    "deaths": side_stat.deaths,
                                    "assists": side_stat.assists,
                                    "kd_diff": side_stat.kd_diff,
                                    "kast": side_stat.kast,
                                    "adr": side_stat.adr,
                                    "hs_percent": side_stat.hs_percent,
                                    "first_kills": side_stat.first_kills,
                                    "first_deaths": side_stat.first_deaths,
                                    "fk_fd_diff": side_stat.fk_fd_diff,
                                })
                            records.append(rec)
                continue

            if side in ("overall", "attack", "defend"):
                for team in (g.team1, g.team2):
                    t_name = team.team_name or "TBD"
                    t_tag = team.team_short or (t_name if t_name == "TBD" else None)
                    for p in team.players:
                        side_stat = getattr(p.stats, side, None)
                        rec = {
                            "series_id": g.series_id or self.series_id,
                            "game_id": g.game_id,
                            "map_name": map_display,
                            "team_id": team.team_id or None,
                            "team_name": t_name,
                            "team_tag": t_tag,
                            "player_id": p.player_id,
                            "name": p.name,
                            "country_code": p.country_code or None,
                            "country": p.country or None,
                            "primary_agent": p.agents[0] if p.agents else None,
                            "agents": list(p.agents),
                            "side": side,
                            "url": f"https://www.vlr.gg/{self.series_id or g.series_id}",
                        }
                        if side_stat is not None:
                            rec.update({
                                "rating": side_stat.rating,
                                "acs": side_stat.acs,
                                "kills": side_stat.kills,
                                "deaths": side_stat.deaths,
                                "assists": side_stat.assists,
                                "kd_diff": side_stat.kd_diff,
                                "kast": side_stat.kast,
                                "adr": side_stat.adr,
                                "hs_percent": side_stat.hs_percent,
                                "first_kills": side_stat.first_kills,
                                "first_deaths": side_stat.first_deaths,
                                "fk_fd_diff": side_stat.fk_fd_diff,
                            })
                        records.append(rec)
                continue

            # Default ('all_splits' / 'wide'): Complete view with overall, attack, and defense side-by-side
            for team in (g.team1, g.team2):
                t_name = team.team_name or "TBD"
                t_tag = team.team_short or (t_name if t_name == "TBD" else None)
                for p in team.players:
                    ov = p.stats.overall
                    att = p.stats.attack
                    defn = p.stats.defend

                    records.append({
                        "series_id": g.series_id or self.series_id,
                        "game_id": g.game_id,
                        "map_name": map_display,
                        "team_id": team.team_id or None,
                        "team_name": t_name,
                        "team_tag": t_tag,
                        "player_id": p.player_id,
                        "name": p.name,
                        "country_code": p.country_code or None,
                        "country": p.country or None,
                        "primary_agent": p.agents[0] if p.agents else None,
                        "agents": list(p.agents),
                        "url": f"https://www.vlr.gg/{self.series_id or g.series_id}",
                        # Overall Stats
                        "rating": ov.rating if ov else None,
                        "acs": ov.acs if ov else None,
                        "kills": ov.kills if ov else None,
                        "deaths": ov.deaths if ov else None,
                        "assists": ov.assists if ov else None,
                        "kd_diff": ov.kd_diff if ov else None,
                        "kast": ov.kast if ov else None,
                        "adr": ov.adr if ov else None,
                        "hs_percent": ov.hs_percent if ov else None,
                        "first_kills": ov.first_kills if ov else None,
                        "first_deaths": ov.first_deaths if ov else None,
                        "fk_fd_diff": ov.fk_fd_diff if ov else None,
                        # Attack Stats
                        "attack_rating": att.rating if att else None,
                        "attack_acs": att.acs if att else None,
                        "attack_kills": att.kills if att else None,
                        "attack_deaths": att.deaths if att else None,
                        "attack_assists": att.assists if att else None,
                        "attack_kd_diff": att.kd_diff if att else None,
                        "attack_kast": att.kast if att else None,
                        "attack_adr": att.adr if att else None,
                        "attack_hs_percent": att.hs_percent if att else None,
                        "attack_first_kills": att.first_kills if att else None,
                        "attack_first_deaths": att.first_deaths if att else None,
                        "attack_fk_fd_diff": att.fk_fd_diff if att else None,
                        # Defense Stats
                        "defend_rating": defn.rating if defn else None,
                        "defend_acs": defn.acs if defn else None,
                        "defend_kills": defn.kills if defn else None,
                        "defend_deaths": defn.deaths if defn else None,
                        "defend_assists": defn.assists if defn else None,
                        "defend_kd_diff": defn.kd_diff if defn else None,
                        "defend_kast": defn.kast if defn else None,
                        "defend_adr": defn.adr if defn else None,
                        "defend_hs_percent": defn.hs_percent if defn else None,
                        "defend_first_kills": defn.first_kills if defn else None,
                        "defend_first_deaths": defn.first_deaths if defn else None,
                        "defend_fk_fd_diff": defn.fk_fd_diff if defn else None,
                    })
        return records
