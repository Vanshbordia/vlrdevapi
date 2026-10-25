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


def test_missing_dependency_error_on_to_polars() -> None:
    """Verify that calling .to_polars() without polars raises MissingDependencyError."""
    class SampleModel(ExportableModel):
        val: int = 42

    model = SampleModel()
    with patch("builtins.__import__", side_effect=ImportError("No module named 'polars'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            model.to_polars()
        assert "polars is required" in str(exc_info.value)
        assert "vlrdevapi[polars]" in str(exc_info.value)


def test_missing_dependency_error_on_to_excel() -> None:
    """Verify that calling .to_excel() without openpyxl raises MissingDependencyError."""
    class SampleModel(ExportableModel):
        val: int = 42

    model = SampleModel()
    with patch("builtins.__import__", side_effect=ImportError("No module named 'openpyxl'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            model.to_excel("dummy.xlsx")
        assert "openpyxl is required" in str(exc_info.value)
        assert "vlrdevapi[excel]" in str(exc_info.value)


def test_missing_dependency_error_on_to_parquet() -> None:
    """Verify that calling .to_parquet() without pyarrow raises MissingDependencyError."""
    class SampleModel(ExportableModel):
        val: int = 42

    model = SampleModel()
    with patch("builtins.__import__", side_effect=ImportError("No module named 'pyarrow'")):
        with pytest.raises(MissingDependencyError) as exc_info:
            model.to_parquet("dummy.parquet")
        assert "pyarrow is required" in str(exc_info.value)
        assert "vlrdevapi[arrow]" in str(exc_info.value)


def test_to_json_in_memory_and_file(tmp_path: Path) -> None:
    """Verify .to_json() string generation and file writing."""
    p1 = PlayerGameStats(
        player_id=3520,
        name="ZmjjKK",
        country="China",
        country_code="cn",
        team_short="EDG",
        agents=["Neon", "Raze"],
    )
    model = PlayersStats(
        series_id=378829,
        game_id="all",
        map_name="All Maps",
        team1=TeamPlayers(team_id=1120, team_name="EDward Gaming", players=[p1]),
    )

    # 1. In-memory JSON records export
    json_str = model.to_json(orient="records")
    assert json_str is not None
    import json
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "ZmjjKK"
    assert data[0]["primary_agent"] == "Neon"
    assert data[0]["agents"] == ["Neon", "Raze"]
    assert isinstance(data[0]["agents"], list)

    # 2. In-memory model tree export
    model_json = model.to_json(orient="model")
    model_data = json.loads(model_json)
    assert isinstance(model_data, dict)
    assert model_data["series_id"] == 378829

    # 3. File export
    target_file = tmp_path / "players.json"
    res = model.to_json(path=target_file)
    assert res is None
    assert target_file.exists()
    file_data = json.loads(target_file.read_text(encoding="utf-8"))
    assert file_data[0]["name"] == "ZmjjKK"


def test_to_dict_export() -> None:
    """Verify .to_dict() returns records list or model dict."""
    roster = TeamRoster(
        players=[Player(id=1, ign="Boaster", roles=["Player", "IGL"])],
    )
    # Default 'records' orient
    recs = roster.to_dict()
    assert isinstance(recs, list)
    assert recs[0]["ign"] == "Boaster"
    assert recs[0]["roles"] == ["Player", "IGL"]
    assert recs[0]["primary_role"] == "Player"

    # 'model' orient
    model_tree = roster.to_dict(orient="model")
    assert isinstance(model_tree, dict)
    assert "players" in model_tree


def test_csv_multivalue_list_formatting(tmp_path: Path) -> None:
    """Verify that list columns are cleanly formatted in CSV with semicolons."""
    records = [
        {"player": "ZmjjKK", "agents": ["Neon", "Raze", "Jett"], "team": "EDG"},
        {"player": "CHICHOO", "agents": ["Cypher"], "team": "EDG"},
    ]
    target_csv = tmp_path / "agents.csv"
    records_to_csv(records, path=target_csv)
    lines = target_csv.read_text(encoding="utf-8").strip().split("\n")
    assert lines[0] == "player,agents,team"
    assert lines[1] == 'ZmjjKK,Neon; Raze; Jett,EDG'
    assert lines[2] == 'CHICHOO,Cypher,EDG'


def test_series_players_map_segregation_and_polars_parquet(tmp_path: Path) -> None:
    """Verify series players map-by-map segregation, Polars List type, and Parquet roundtrip."""
    map1 = PlayersStats(
        series_id=100,
        game_id="101",
        map_name="Haven",
        team1=TeamPlayers(
            team_id=1,
            team_name="SEN",
            players=[PlayerGameStats(player_id=10, name="TenZ", agents=["Omen"])],
        ),
    )
    overview = PlayersStats(
        series_id=100,
        game_id="all",
        map_name="",
        team1=TeamPlayers(
            team_id=1,
            team_name="SEN",
            players=[PlayerGameStats(player_id=10, name="TenZ", agents=["Omen", "Yoru"])],
        ),
        maps=[map1],
    )

    # Verify to_records outputs Map 1 row then All Maps overview row
    records = overview.to_records()
    assert len(records) == 2
    assert records[0]["map_name"] == "Haven"
    assert records[0]["primary_agent"] == "Omen"
    assert records[0]["agents"] == ["Omen"]
    assert records[1]["map_name"] == "All Maps"
    assert records[1]["primary_agent"] == "Omen"
    assert records[1]["agents"] == ["Omen", "Yoru"]

    # Test Polars List(Utf8) preservation
    try:
        import polars as pl
        pl_df = overview.to_polars()
        assert isinstance(pl_df, pl.DataFrame)
        assert len(pl_df) == 2
        assert pl_df.schema["agents"] == pl.List(pl.String)
    except ImportError:
        pass

    # Test Parquet write and read
    try:
        import pandas as pd
        parquet_file = tmp_path / "players.parquet"
        overview.to_parquet(parquet_file)
        assert parquet_file.exists()
        re_read = pd.read_parquet(parquet_file)
        assert len(re_read) == 2
        assert re_read.iloc[0]["map_name"] == "Haven"
    except ImportError:
        pass


def test_excel_export_roundtrip(tmp_path: Path) -> None:
    """Verify Excel export creates valid .xlsx readable by openpyxl/pandas."""
    try:
        import openpyxl  # noqa: F401
        import pandas as pd
        model = RoundsData(
            series_id=99,
            game_id=1,
            team1="SEN",
            team1_id=1,
            team2="FNC",
            team2_id=2,
            rounds=[
                RoundData(
                    round_number=1,
                    winner_team_name="SEN",
                    winner_team_id=1,
                    win_type=RoundWinType.ELIMINATION,
                    side="Attack",
                    team1_score=1,
                    team2_score=0,
                )
            ],
        )
        xlsx_path = tmp_path / "rounds.xlsx"
        model.to_excel(xlsx_path)
        assert xlsx_path.exists()
        df = pd.read_excel(xlsx_path)
        assert len(df) == 1
        assert df.iloc[0]["winner_name"] == "SEN"
    except ImportError:
        pass


def test_records_to_markdown_pipe_escaping() -> None:
    """Verify that pipe characters inside cells and columns are properly escaped with backslash."""
    records = [
        {"title": "SEN vs FNC | Map 1 Highlights | Grand Final", "note": "score: 13 | 11"},
        {"title": "Normal title", "note": "clean note"},
    ]
    md = records_to_markdown(records)
    lines = md.strip().split("\n")
    assert len(lines) == 4
    assert r"SEN vs FNC \| Map 1 Highlights \| Grand Final" in lines[2]
    assert r"score: 13 \| 11" in lines[2]


def test_excel_sheet_name_support(tmp_path: Path) -> None:
    """Verify that to_excel respects the custom sheet_name parameter."""
    try:
        import openpyxl
        import pandas as pd
        model = RoundsData(
            series_id=99,
            game_id=1,
            team1="SEN",
            team1_id=1,
            team2="FNC",
            team2_id=2,
            rounds=[
                RoundData(
                    round_number=1,
                    winner_team_name="SEN",
                    winner_team_id=1,
                    win_type=RoundWinType.ELIMINATION,
                    side="Attack",
                    team1_score=1,
                    team2_score=0,
                )
            ],
        )
        xlsx_path = tmp_path / "custom_sheet.xlsx"
        model.to_excel(xlsx_path, sheet_name="PlayerStats")
        assert xlsx_path.exists()
        wb = openpyxl.load_workbook(xlsx_path)
        assert "PlayerStats" in wb.sheetnames
    except ImportError:
        pass


def test_empty_buy_tier_does_not_crash_buy_matrix_export() -> None:
    """Verify that EconomyData with None or empty buy matrix does not raise AttributeError."""
    model = EconomyData(
        series_id=500,
        game_id=1,
        team1="SEN",
        team1_id=1,
        team2="FNC",
        team2_id=2,
        buy_matrix_team1=None,
        buy_matrix_team2=None,
        rounds=[],
    )
    records = model.to_records(view="buy_matrix")
    assert records == []


def test_players_stats_kd_calculation_with_none_or_zero() -> None:
    """Verify that players with None kills, None deaths, or 0 deaths do not crash export."""
    p_none_kills = PlayerGameStats(
        player_id=1,
        name="PlayerNoneKills",
        stats=PlayerStats(
            overall=SideStats(kills=None, deaths=5),
            attack=SideStats(kills=None, deaths=2),
            defend=SideStats(kills=None, deaths=3),
        ),
    )
    p_zero_deaths = PlayerGameStats(
        player_id=2,
        name="PlayerZeroDeaths",
        stats=PlayerStats(
            overall=SideStats(kills=10, deaths=0),
            attack=SideStats(kills=6, deaths=0),
            defend=SideStats(kills=4, deaths=0),
        ),
    )
    p_none_deaths = PlayerGameStats(
        player_id=3,
        name="PlayerNoneDeaths",
        stats=PlayerStats(
            overall=SideStats(kills=10, deaths=None),
        ),
    )
    stats = PlayersStats(
        series_id=100,
        game_id="all",
        team1=TeamPlayers(team_id=10, team_name="Team A", players=[p_none_kills, p_zero_deaths, p_none_deaths]),
        team2=TeamPlayers(team_id=20, team_name="Team B", players=[]),
    )

    # Wide view
    records_wide = stats.to_records(side="wide")
    assert records_wide[0]["kd"] is None
    assert records_wide[1]["kd"] == 10.0
    assert records_wide[2]["kd"] is None

    # Single-side view
    records_overall = stats.to_records(side="overall")
    assert records_overall[0]["kd"] is None
    assert records_overall[1]["kd"] == 10.0
    assert records_overall[2]["kd"] is None

    # Split view
    records_split = stats.to_records(side="split")
    assert records_split[0]["kd"] is None

