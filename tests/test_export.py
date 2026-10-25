"""Unit tests for the multi-format export system (CSV, Markdown, DataFrames, etc.)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from vlrdevapi._matches.upcoming.models import (
    TeamInUpcomingMatch,
    UpcomingMatchEntry,
    UpcomingMatchesPage,
)
from vlrdevapi._series.economy.models import EconomyData, RoundEconomyData, RoundWinner
from vlrdevapi._series.players.models import (
    PlayerGameStats,
    PlayersStats,
    PlayerStats,
    SideStats,
    TeamPlayers,
)
from vlrdevapi._series.rounds.models import RoundData, RoundsData, RoundWinType
from vlrdevapi._team.roster.models import Player, TeamRoster
from vlrdevapi.commons.export import (
    ExportableModel,
    records_to_csv,
    records_to_markdown,
)
from vlrdevapi.exceptions import MissingDependencyError


def test_records_to_csv_in_memory() -> None:
    """Verify in-memory CSV generation."""
    records = [
        {"name": "Boaster", "team": "FNC", "acs": 210.5},
        {"name": "Chronicle", "team": "FNC", "acs": 235.0},
    ]
    csv_str = records_to_csv(records)
    assert csv_str is not None
    lines = csv_str.strip().split("\n")
    assert lines[0] == "name,team,acs"
    assert lines[1] == "Boaster,FNC,210.5"
    assert lines[2] == "Chronicle,FNC,235.0"


def test_records_to_csv_file_write(tmp_path: Path) -> None:
    """Verify writing CSV to a file path."""
    records = [{"ign": "Derke", "kills": 24}]
    target_file = tmp_path / "stats.csv"
    res = records_to_csv(records, path=target_file)
    assert res is None
    assert target_file.exists()
    content = target_file.read_text(encoding="utf-8").strip()
    assert content == "ign,kills\nDerke,24"


def test_records_to_markdown_alignment() -> None:
    """Verify Markdown table generation and column alignment."""
    records = [
        {"player": "Derke", "team": "FNC", "acs": 260},
        {"player": "Alfajer", "team": "FNC", "acs": 245},
    ]
    md = records_to_markdown(records)
    lines = md.split("\n")
    assert len(lines) == 4  # Header, separator, 2 data lines
    assert "| player" in lines[0]
    assert "| ---" in lines[1]
    assert "| Derke" in lines[2]
    assert "| Alfajer" in lines[3]


def test_players_stats_flattening() -> None:
    """Verify domain-aware flattening of series player stats."""
    p1 = PlayerGameStats(
        player_id=11225,
        name="TenZ",
        country="Canada",
        country_code="CA",
        team_short="SEN",
        agents=["Omen"],
        stats=PlayerStats(
            overall=SideStats(rating=1.25, acs=240.0, kills=20, deaths=14, assists=10),
            attack=SideStats(rating=1.35, kills=12),
            defend=SideStats(rating=1.15, kills=8),
        ),
    )
    model = PlayersStats(
        series_id=100,
        game_id="1",
        map_name="Haven",
        team1=TeamPlayers(team_id=1, team_name="Sentinels", team_short="SEN", players=[p1]),
        team2=TeamPlayers(team_id=2, team_name="FNATIC", team_short="FNC", players=[]),
    )

    # Test default overall records
    records = model.to_records(side="overall")
    assert len(records) == 1
    assert records[0]["player_id"] == 11225
    assert records[0]["name"] == "TenZ"
    assert records[0]["map_name"] == "Haven"
    assert records[0]["acs"] == 240.0
    assert records[0]["kills"] == 20

    # Test side="all" (produces 3 rows: overall, attack, defend)
    records_all = model.to_records(side="all")
    assert len(records_all) == 3
    sides = [r["side"] for r in records_all]
    assert sides == ["overall", "attack", "defend"]
    assert records_all[1]["kills"] == 12  # Attack kills


def test_economy_data_flattening() -> None:
    """Verify domain-aware flattening of round economy data."""
    model = EconomyData(
        series_id=200,
        game_id="1",
        team1="Sentinels",
        team1_id=1,
        team2="FNATIC",
        team2_id=2,
        rounds=[
            RoundEconomyData(
                round_number=1,
                winner=RoundWinner(name="Sentinels", id=1),
                spent_team1=3800,
                bank_team1=150,
                spent_team2=3700,
                bank_team2=200,
                is_pistol_round=True,
            )
        ],
    )

    records = model.to_records(view="rounds")
    assert len(records) == 1
    assert records[0]["round_number"] == 1
    assert records[0]["winner_name"] == "Sentinels"
    assert records[0]["team1_spent"] == 3800
    assert records[0]["is_pistol_round"] is True


def test_rounds_data_flattening() -> None:
    """Verify domain-aware flattening of round results."""
    model = RoundsData(
        series_id=300,
        game_id=1,
        team1="Paper Rex",
        team1_id=10,
        team2="Gen.G",
        team2_id=20,
        rounds=[
            RoundData(
                round_number=1,
                winner_team_name="Paper Rex",
                winner_team_id=10,
                win_type=RoundWinType.ELIMINATION,
                side="Attack",
                team1_score=1,
                team2_score=0,
                is_pistol_round=True,
            )
        ],
    )

    records = model.to_records()
    assert len(records) == 1
    assert records[0]["round_number"] == 1
    assert records[0]["winner_name"] == "Paper Rex"
    assert records[0]["win_type"] == "elimination"
    assert records[0]["side"] == "Attack"


def test_upcoming_matches_page_flattening() -> None:
    """Verify flattening of upcoming matches list."""
    match = UpcomingMatchEntry(
        match_id=999,
        event="VCT Champions",
        stage="Playoffs",
        status="upcoming",
        eta="2h",
        team1=TeamInUpcomingMatch(id=1, name="Sentinels", tag="SEN", country_name="United States"),
        team2=TeamInUpcomingMatch(id=2, name="FNATIC", tag="FNC", country_name="United Kingdom"),
        url="/999/match",
    )
    page = UpcomingMatchesPage(matches=[match], has_next_page=False)

    records = page.to_records()
    assert len(records) == 1
    assert records[0]["match_id"] == 999
    assert records[0]["team1_name"] == "Sentinels"
    assert records[0]["team2_tag"] == "FNC"
    assert records[0]["eta"] == "2h"


def test_team_roster_flattening() -> None:
    """Verify flattening of team roster."""
    roster = TeamRoster(
        players=[Player(id=1, ign="Boaster", real_name="Jake", country="UK", roles=["Player", "IGL"])],
        staff=[Player(id=2, ign="mini", real_name="Rodrigo", country="UK", roles=["Coach"])],
    )
    records = roster.to_records(include_staff=True)
    assert len(records) == 2
    assert records[0]["ign"] == "Boaster"
    assert records[0]["roles"] == ["Player", "IGL"]
    assert records[0]["primary_role"] == "Player"
    assert records[1]["ign"] == "mini"
    assert records[1]["roles"] == ["Coach"]
    assert records[1]["primary_role"] == "Coach"


def test_to_df_and_to_polars_integration() -> None:
    """Verify DataFrame and Polars conversion when libraries are present."""
    match = UpcomingMatchEntry(
        match_id=123,
        event="VCT Masters",
        stage="Grand Final",
        status="upcoming",
        eta="1h 30m",
        team1=TeamInUpcomingMatch(id=1, name="Sentinels", tag="SEN", country_name="USA"),
        team2=TeamInUpcomingMatch(id=2, name="FNATIC", tag="FNC", country_name="UK"),
        url="/123/match",
    )
    page = UpcomingMatchesPage(matches=[match])

    # Test Pandas
    try:
        import pandas as pd
        df = page.to_df()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["team1_name"] == "Sentinels"
    except ImportError:
        pass

    # Test Polars
    try:
        import polars as pl
        pl_df = page.to_polars()
        assert isinstance(pl_df, pl.DataFrame)
        assert len(pl_df) == 1
        assert pl_df["team1_name"][0] == "Sentinels"
    except ImportError:
        pass


def test_missing_dependency_error_on_to_df() -> None:
    """Verify that calling .to_df() when pandas is not installed raises MissingDependencyError."""
    class SampleModel(ExportableModel):
        val: int = 42

    model = SampleModel()
    with patch("builtins.__import__", side_effect=ImportError("No module named 'pandas'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            model.to_df()
        assert "pandas is required" in str(exc_info.value)
        assert "vlrdevapi[pandas]" in str(exc_info.value)
