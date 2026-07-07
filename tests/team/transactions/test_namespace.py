from datetime import date

from tests.conftest import load_fixture
from tests.conftest import mock_vlr  # noqa: F401
import vlrdevapi
from vlrdevapi._team.transactions.models import TransactionAction


class TestSyncModuleLevel:
    def test_team_transactions_nrg(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))

        result = vlrdevapi.team.transactions(1034)
        assert result.team_id == 1034
        assert len(result.transactions) > 0

        txn = result.transactions[0]
        assert txn.date is not None
        assert txn.player.id > 0
        assert txn.player.ign
        assert txn.player.country
        assert txn.position
        assert txn.action in [
            TransactionAction.Join,
            TransactionAction.Leave,
            TransactionAction.Inactive,
        ]


class TestSyncWithClient:
    def test_team_transactions_curried(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team(1034).transactions()
        assert result.team_id == 1034
        assert len(result.transactions) > 0

    def test_team_transactions_direct(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team.transactions(1034)
        assert result.team_id == 1034
        assert len(result.transactions) > 0

    def test_team_transactions_100_thieves(self, mock_vlr):
        mock_vlr.get("/team/transactions/120/").respond(200, text=load_fixture("team", "120", "transactions.html"))

        with vlrdevapi.VLRClient() as client:
            result = client.team.transactions(120)
        assert result.team_id == 120
        assert len(result.transactions) >= 0
class TestTransactionData:
    def test_transaction_action_values(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))
        result = vlrdevapi.team.transactions(1034)

        for txn in result.transactions:
            assert txn.action.value in ["Join", "Leave", "Inactive"]

    def test_transaction_player_data_complete(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))
        result = vlrdevapi.team.transactions(1034)

        for txn in result.transactions:
            assert txn.player.id > 0
            assert txn.player.ign
            assert txn.player.country

    def test_transaction_dates_valid(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))
        result = vlrdevapi.team.transactions(1034)

        for txn in result.transactions:
            if txn.date:
                assert isinstance(txn.date, date)
                assert txn.date.year >= 2020
                assert txn.date.year <= 2030

    def test_transaction_positions(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))
        result = vlrdevapi.team.transactions(1034)

        for txn in result.transactions:
            assert txn.position

    def test_first_transaction_details(self, mock_vlr):
        mock_vlr.get("/team/transactions/1034/").respond(200, text=load_fixture("team", "1034", "transactions.html"))
        result = vlrdevapi.team.transactions(1034)
        if len(result.transactions) > 0:
            first = result.transactions[0]
            assert first.date is not None
            assert isinstance(first.date, date)
            assert first.player.id > 0
            assert len(first.player.ign) > 0
            assert len(first.player.country) > 2

