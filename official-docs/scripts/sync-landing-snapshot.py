r"""Regenerate the landing page's real VLR.gg snapshot.

Run from the repository root:

    .\.venv\Scripts\python.exe official-docs\scripts\sync-landing-snapshot.py

The landing page is a static export, so this keeps its previews grounded in
real VLR.gg data without making the docs build depend on Python or the network.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

from vlrdevapi import VLRClient
from vlrdevapi.fetcher import DEFAULT_HEADERS

OUTPUT = Path(__file__).resolve().parents[1] / "components" / "landing" / "landing-snapshot.json"


def first_paragraph(text: str) -> str:
    for block in text.split("\n\n"):
        block = block.strip()
        if block:
            return block
    return ""


def main() -> None:
    with VLRClient() as client:
        player = client.player(11225)
        player_info = player.info()
        player_profile = player.profile()
        player_agents = player.agents(timespan="90d")

        team = client.team(1034)
        team_info = team.info()
        roster = team.roster()
        placements = team.placements()

        series = client.series(542272)
        series_info = series.info()
        series_vods = series.vods()

        event = client.event(2863)
        event_info = event.info()
        event_stages = event.stages()
        event_standings = event.standings()

        news_page = client.news(page=1)
        news_item = news_page.news[0]
        article = client.news.article(news_item.id)

    player_html = httpx.get(
        "https://www.vlr.gg/player/11225",
        headers=DEFAULT_HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    player_html.raise_for_status()

    team_highlight = next(
        (
            placement
            for placement in placements.placements
            if any(row.placement == "1st" for row in placement.placements)
        ),
        placements.placements[0],
    )
    team_highlight_row = next(
        (row for row in team_highlight.placements if row.placement == "1st"),
        team_highlight.placements[0],
    )

    playoff_stage = next(
        (stage for stage in event_standings.stages if stage.stage_name == "Playoffs"),
        event_standings.stages[0],
    )

    data = {
        "capturedAt": datetime.now(UTC).strftime("%Y-%m-%d"),
        "player": {
            "id": player_info.player_id,
            "name": player_info.name,
            "realName": player_info.real_name,
            "country": player_info.country,
            "team": player_profile.current_team.name if player_profile.current_team else "",
            "totalWinnings": player_info.total_winnings,
            "currency": player_info.total_winnings_currency,
            "fieldCount": len(type(player_info).model_fields),
            "requestBytes": len(player_html.content),
            "agents": [
                {
                    "name": agent.agent,
                    "share": agent.use.split(") ")[-1],
                    "rounds": agent.rounds,
                    "rating": agent.rating,
                    "acs": agent.acs,
                    "kd": agent.kd,
                }
                for agent in player_agents.agents[:3]
            ],
        },
        "team": {
            "id": team_info.id,
            "name": team_info.name,
            "country": team_info.country,
            "totalWinnings": placements.total_winnings,
            "currency": placements.total_winnings_currency,
            "players": [
                {
                    "id": member.id,
                    "ign": member.ign,
                    "realName": member.real_name,
                    "country": member.country,
                    "role": "Captain" if member.is_captain else "Player",
                }
                for member in roster.players
            ],
            "staff": [
                {
                    "ign": member.ign,
                    "role": member.roles[0] if member.roles else "Staff",
                }
                for member in roster.staff
            ],
            "highlight": {
                "event": team_highlight.event_name,
                "stage": team_highlight_row.stage,
                "placement": team_highlight_row.placement,
            },
        },
        "series": {
            "id": series_info.series_id,
            "team1": series_info.team1.name,
            "team2": series_info.team2.name,
            "score1": series_info.score1,
            "score2": series_info.score2,
            "bestOf": series_info.best_of,
            "event": series_info.event_name,
            "stage": series_info.stage,
            "bracket": series_info.bracket,
            "datetime": series_info.datetime.isoformat() if series_info.datetime else None,
            "patch": series_info.patch,
            "rounds": sum(
                game.team1_score + game.team2_score
                for game in series_info.games
                if game.played
            ),
            "vods": len(series_vods.vods),
            "maps": [
                {
                    "map": game.map_name,
                    "score1": game.team1_score,
                    "score2": game.team2_score,
                    "pickedBy": game.picked_by or "Decider",
                }
                for game in series_info.games
                if game.played
            ],
        },
        "event": {
            "id": event_info.id,
            "name": event_info.name,
            "region": event_info.regions[0].name if event_info.regions else "",
            "venue": event_info.location.venue,
            "country": event_info.location.country,
            "startDate": event_info.start_date.strftime("%Y-%m-%d"),
            "endDate": event_info.end_date.strftime("%Y-%m-%d"),
            "stages": [
                {
                    "name": stage.name,
                    "startDate": str(stage.start_date) if stage.start_date else None,
                    "endDate": str(stage.end_date) if stage.end_date else None,
                }
                for stage in event_stages.stages
            ],
            "standings": [
                {
                    "place": row.place,
                    "team": row.team.name,
                    "points": row.points,
                }
                for row in playoff_stage.standings[:3]
            ],
        },
        "news": {
            "id": news_item.id,
            "title": news_item.title,
            "subtitle": news_item.subtitle,
            "author": news_item.author,
            "date": news_item.date.isoformat() if news_item.date else None,
            "country": news_item.country_name,
            "excerpt": first_paragraph(article.content)[:360],
            "contentLength": len(article.content_md),
            "links": article.content_md.count("]("),
        },
    }

    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
