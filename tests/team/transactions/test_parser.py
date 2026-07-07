from datetime import datetime, timezone

import pytest
from selectolax.parser import HTMLParser, Node

from tests.conftest import FIXTURES_DIR, _LIVE, live_fetch
from tests.helpers.fixtures import transaction_date_from_row
from vlrdevapi._team.transactions.parser import (
    parse_team_transactions,
    _parse_transaction_row,
)
from vlrdevapi._team.transactions.models import TransactionAction

_FIXTURES = FIXTURES_DIR / "team"


def _load_html(team_id: int, filename: str) -> HTMLParser:
    if _LIVE:
        return HTMLParser(live_fetch(f"/team/transactions/{team_id}/"))
    path = _FIXTURES / str(team_id) / filename
    if path.exists():
        return HTMLParser(path.read_text(encoding="utf-8"))
    pytest.fail(f"Fixture not found: {path}")


def _get_table_rows(html: HTMLParser) -> list[Node]:
    table = html.css_first("table.wf-faux-table")
    assert table is not None
    return table.css("tr.txn-item")


class TestParseTransactionRow:
    def test_parse_first_transaction(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)
        assert len(rows) > 0

        txn = _parse_transaction_row(rows[0])
        assert txn is not None
        assert txn.date == transaction_date_from_row(rows[0])
        assert txn.action == TransactionAction.Join
        assert txn.player.id == 612
        assert txn.player.ign == "mitch"
        assert txn.player.real_name == "Mitch Semago"
        assert txn.player.country == "United States"
        assert txn.position == "Assistant coach"
        assert "x.com/NRGgg" in txn.source_url

    def test_parse_join_transaction(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)

        txn = _parse_transaction_row(rows[2])
        assert txn is not None
        assert txn.date == transaction_date_from_row(rows[2])
        assert txn.action == TransactionAction.Join
        assert txn.player.id == 11494
        assert txn.player.ign == "keiko"
        assert txn.player.real_name == "Georgio Sanassy"
        assert txn.player.country == "United Kingdom"
        assert txn.position == "Player"

    def test_parse_us_player(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)

        txn = _parse_transaction_row(rows[3])
        assert txn is not None
        assert txn.player.id == 4164
        assert txn.player.ign == "s0m"
        assert txn.player.real_name == "Sam Oh"
        assert txn.player.country == "United States"

    def test_parse_canadian_player(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)

        txn = _parse_transaction_row(rows[4])
        assert txn is not None
        assert txn.player.id == 817
        assert txn.player.ign == "FiNESSE"
        assert txn.player.real_name == "Pujan Mehta"
        assert txn.player.country == "Canada"

    def test_parse_inactive_transaction(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)

        for row in rows:
            txn = _parse_transaction_row(row)
            if txn and txn.action == TransactionAction.Inactive:
                assert txn.action == TransactionAction.Inactive
                assert txn.player.ign
                return

        pytest.skip("No inactive transaction found in fixture")

    def test_parse_all_transaction_rows(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)

        for row in rows:
            txn = _parse_transaction_row(row)
            if txn:
                assert txn.player.id > 0
                assert txn.player.ign
                assert txn.action in [
                    TransactionAction.Join,
                    TransactionAction.Leave,
                    TransactionAction.Inactive,
                ]


class TestParseTeamTransactions:
    def test_parse_nrg_transactions(self):
        html = _load_html(1034, "transactions.html")
        rows = _get_table_rows(html)
        result = parse_team_transactions(html, 1034)

        assert result.team_id == 1034
        assert len(result.transactions) == 85

        first = result.transactions[0]
        assert first.date == transaction_date_from_row(rows[0])
        assert first.action == TransactionAction.Join
        assert first.player.id == 612
        assert first.player.ign == "mitch"
        assert first.player.real_name == "Mitch Semago"
        assert first.player.country == "United States"
        assert first.position == "Assistant coach"

    def test_parse_empty_table(self):
        html = HTMLParser("<table class='wf-faux-table'></table>")
        result = parse_team_transactions(html, 99999)

        assert result.team_id == 99999
        assert len(result.transactions) == 0

    def test_transaction_date_format(self):
        html = _load_html(1034, "transactions.html")
        result = parse_team_transactions(html, 1034)

        for txn in result.transactions:
            if txn.date:
                assert txn.date.year >= 2020
                assert txn.date.year <= 2026
                assert 1 <= txn.date.month <= 12
                assert 1 <= txn.date.day <= 31

    def test_transaction_actions_variety(self):
        html = _load_html(1034, "transactions.html")
        result = parse_team_transactions(html, 1034)

        actions_found = {txn.action for txn in result.transactions}
        assert TransactionAction.Join in actions_found
        assert TransactionAction.Leave in actions_found
        assert TransactionAction.Inactive in actions_found

    def test_player_countries_variety(self):
        html = _load_html(1034, "transactions.html")
        result = parse_team_transactions(html, 1034)

        countries = {txn.player.country for txn in result.transactions}
        assert "United States" in countries
        assert "United Kingdom" in countries
        assert "Canada" in countries

    def test_positions_variety(self):
        html = _load_html(1034, "transactions.html")
        result = parse_team_transactions(html, 1034)

        positions = {txn.position for txn in result.transactions}
        assert "Player" in positions
        assert "Assistant coach" in positions

    def test_source_urls(self):
        html = _load_html(1034, "transactions.html")
        result = parse_team_transactions(html, 1034)

        with_source = [t for t in result.transactions if t.source_url]
        assert len(with_source) > 0

        for txn in with_source:
            assert txn.source_url.startswith("http")

    def test_unknown_date_handled(self):
        html = _load_html(1034, "transactions.html")
        result = parse_team_transactions(html, 1034)

        unknown_date_txns = [t for t in result.transactions if t.date is None]
        assert len(unknown_date_txns) == 1

        txn = unknown_date_txns[0]
        assert txn.player.ign == "Ry"
        assert txn.position == "Manager"

