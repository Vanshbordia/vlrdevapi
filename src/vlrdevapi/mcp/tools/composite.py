"""Composite / multi-step workflow tools designed specifically for AI agents.

These tools combine multiple lower-level API calls into single rich responses,
saving LLM agent turns, tokens, and round-trips.
"""

from __future__ import annotations

import vlrdevapi
from vlrdevapi.mcp._common import MCPServer, handle_errors


def register_composite_tools(server: MCPServer) -> None:
    """Register composite multi-endpoint tools."""

    @server.tool()
    @handle_errors
    def get_match_full_context(series_id: int) -> str:
        """Fetch complete context for a match: overview, scores, player ACS stats, and VODs in a single call.

        Designed for AI analysts to immediately summarize or analyze a match without multiple tool turns.

        Args:
            series_id: Unique VLR.gg series identifier.
        """
        match = vlrdevapi.series(series_id)
        info = match.info()
        players = match.players(game_id="all")
        vods = match.vods()

        return {
            "overview": info.to_dict(orient="model"),
            "player_statistics": players.to_dict(orient="model"),
            "vods": vods.to_dict(orient="model"),
        }

    @server.tool()
    @handle_errors
    def get_team_overview(team_id: int) -> str:
        """Get an all-in-one dossier for a team: info, active roster, upcoming schedule, and placements.

        Args:
            team_id: Unique VLR.gg team identifier.
        """
        team = vlrdevapi.team(team_id)
        info = team.info()
        roster = team.roster()
        upcoming = team.upcoming_matches()
        placements = team.placements()

        return {
            "info": info.to_dict(orient="model"),
            "roster": roster.to_dict(orient="model"),
            "upcoming_matches": upcoming.to_dict(orient="model"),
            "placements": placements.to_dict(orient="model"),
        }

    @server.tool()
    @handle_errors
    def compare_teams(team_id_1: int, team_id_2: int, last_days: int = 60) -> str:
        """Compare two teams head-to-head: rosters, recent map statistics, and forms.

        Ideal for AI agents analyzing upcoming matchups or generating pre-match reports.

        Args:
            team_id_1: First team VLR ID.
            team_id_2: Second team VLR ID.
            last_days: Days of recent map performance to compare (default 60).
        """
        t1 = vlrdevapi.team(team_id_1)
        t2 = vlrdevapi.team(team_id_2)

        return {
            "team_1": {
                "info": t1.info().to_dict(orient="model"),
                "roster": t1.roster().to_dict(orient="model"),
                "stats": t1.stats(last_days=last_days).to_dict(orient="model"),
            },
            "team_2": {
                "info": t2.info().to_dict(orient="model"),
                "roster": t2.roster().to_dict(orient="model"),
                "stats": t2.stats(last_days=last_days).to_dict(orient="model"),
            },
        }

    @server.tool()
    @handle_errors
    def get_player_career_summary(player_id: int) -> str:
        """Comprehensive career profile and scouting report for a pro Valorant player.

        Combines profile, agent statistics, tournament placements, and team history into one dossier.

        Args:
            player_id: Unique VLR.gg player identifier.
        """
        p = vlrdevapi.player(player_id)
        return {
            "profile": p.profile().to_dict(orient="model"),
            "agent_stats": p.agents(timespan="all").to_dict(orient="model"),
            "placements": p.placements().to_dict(orient="model"),
            "teams_history": p.teams().to_dict(orient="model"),
        }

    @server.tool()
    @handle_errors
    def get_h2h_matchup(team_id_1: int, team_id_2: int, limit: int = 50) -> str:
        """Analyze direct head-to-head match history and recent records between two teams.

        Args:
            team_id_1: First team VLR ID.
            team_id_2: Second team VLR ID.
            limit: Past matches to inspect for head-to-head encounters (default 50).
        """
        t1 = vlrdevapi.team(team_id_1)
        t2 = vlrdevapi.team(team_id_2)
        m1 = t1.completed_matches(limit=limit)
        direct_matches = [
            m for m in m1.to_records()
            if m.get("opponent_id") == team_id_2
        ]
        return {
            "team_1": {"id": team_id_1, "name": t1.info().name},
            "team_2": {"id": team_id_2, "name": t2.info().name},
            "head_to_head_matches_found": len(direct_matches),
            "matches": direct_matches,
        }

    @server.tool()
    @handle_errors
    def get_tournament_dossier(event_id: int) -> str:
        """Complete tournament dossier: overview details, stages, participating teams, and standings.

        Args:
            event_id: Unique VLR.gg tournament/event identifier.
        """
        ev = vlrdevapi.event(event_id)
        return {
            "info": ev.info().to_dict(orient="model"),
            "stages": ev.stages().to_dict(orient="model"),
            "standings": ev.standings().to_dict(orient="model"),
            "teams": ev.teams().to_dict(orient="model"),
        }

    @server.tool()
    @handle_errors
    def get_live_and_upcoming_schedule(limit: int = 15) -> str:
        """Instant esports schedule: currently live matches followed by upcoming scheduled matches.

        Args:
            limit: Maximum upcoming matches to include (default 15).
        """
        live = vlrdevapi.matches.live()
        upcoming = vlrdevapi.matches.upcoming()
        up_records = upcoming.to_records()[:limit] if hasattr(upcoming, "to_records") else []
        return {
            "live_matches": live.to_dict(orient="model"),
            "upcoming_matches": up_records,
        }

    @server.tool()
    @handle_errors
    def get_news_digest(limit: int = 5, include_top_article_body: bool = True) -> str:
        """Executive Valorant esports news digest: recent headlines and full content of the top article.

        Args:
            limit: Number of recent news items to summarize (default 5).
            include_top_article_body: If True, fetches full text and Markdown for the latest article.
        """
        news = vlrdevapi.news(page=1)
        news_recs = news.to_records()[:limit] if hasattr(news, "to_records") else []
        top_article = None
        if include_top_article_body and news_recs:
            top_id = news_recs[0].get("id")
            if top_id:
                top_article = vlrdevapi.news.article(top_id).to_dict(orient="model")
        return {
            "headlines": news_recs,
            "latest_full_article": top_article,
        }
