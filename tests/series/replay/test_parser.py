import math
from functools import lru_cache

import pytest
from selectolax.lexbor import LexborHTMLParser

from tests.conftest import load_fixture
from vlrdevapi._series.replay.models import ReplayEventType
from vlrdevapi._series.replay.parser import parse_replay_data

DIR_283288 = "754737_loud-vs-team-vitality-valorant-champions-2026-gf"
DIR_283305 = "754742_100-thieves-vs-g2-esports-valorant-champions-2026-lr3"
DIR_286701 = "754743_team-vitality-vs-100-thieves-valorant-champions-2026-lbf"
DIR_180437 = "378829_edward-gaming-vs-team-heretics-valorant-champions-2024-gf"


@lru_cache
def _parse(dir_name: str, game_id: int):
    html = LexborHTMLParser(load_fixture("series", dir_name, f"game_{game_id}_logs.html"))
    return parse_replay_data(html, game_id=game_id)


def _type_counts(data) -> dict[str, int]:
    counts: dict[str, int] = {}
    for rd in data.rounds:
        for ev in rd.events:
            counts[ev.type.value] = counts.get(ev.type.value, 0) + 1
    return counts


class TestChampions2026GFSunset:
    """Game 283288 (LOUD vs Team Vitality, Sunset 13-5)."""

    @property
    def data(self):
        return _parse(DIR_283288, 283288)

    def test_top_level(self):
        assert self.data.team1 == "LOUD"
        assert self.data.team2 == "Team Vitality"
        assert self.data.num_rounds == 18
        assert len(self.data.rounds) == 18
        # Player/team IDs stay 0 until the namespace layer enriches them.
        assert self.data.team1_id == 0
        assert self.data.team2_id == 0
        assert self.data.round(1).players[0].player_id == 0

    def test_round_accessor(self):
        assert self.data.round(9).round_number == 9
        assert self.data.round(999) is None

    def test_attacking_team(self):
        assert self.data.round(1).attacking == "Team Vitality"
        # Second half: LOUD attacks (rounds 13+)
        assert self.data.round(13).attacking == "LOUD"

    def test_round_players(self):
        players = self.data.round(1).players
        assert len(players) == 10
        assert [p.name for p in players[:5]] == ["erde", "tkzin", "Darker", "DaviH", "lukxo"]
        assert players[0].agent == "sage"
        assert players[0].team == "LOUD"
        assert players[0].side == "Defense"
        assert players[5].name == "Chronicle"
        assert players[5].agent == "neon"
        assert players[5].team == "Team Vitality"
        assert players[5].side == "Attack"

    def test_first_kill_details(self):
        ev = self.data.round(1).events[0]
        assert ev.seq == 0
        assert ev.type is ReplayEventType.KILL
        assert ev.clock == "0:19"
        assert ev.seconds == 19
        assert ev.actor.name == "tkzin"
        assert ev.actor.agent == "neon"
        assert ev.actor.team == "LOUD"
        assert ev.actor.side == "Defense"
        assert ev.victim.name == "Jamppi"
        assert ev.victim.agent == "kayo"
        assert ev.victim.team == "Team Vitality"
        assert ev.cause == "Sheriff"
        assert (ev.from_x, ev.from_y) == (236.9, 492.7)
        assert (ev.pos_x, ev.pos_y) == (167.7, 487.2)
        assert ev.distance_units == pytest.approx(math.dist((236.9, 492.7), (167.7, 487.2)))
        assert ev.derived is False

    def test_alive_snapshot(self):
        alive = self.data.round(1).events[0].alive
        assert len(alive) == 9  # victim Jamppi already excluded
        first = alive[0]
        assert first.name == "Derke"
        assert first.agent == "chamber"
        assert first.team == "Team Vitality"
        assert first.side == "Attack"
        assert (first.x, first.y) == (148.5, 612.6)
        assert first.view_angle == 246
        assert all(a.name != "Jamppi" for a in alive)

    def test_spike_plant(self):
        ev = self.data.round(1).events[8]
        assert ev.type is ReplayEventType.PLANT
        assert ev.clock == "0:43"
        assert ev.seconds == 43
        assert ev.actor.name == "PROFEK"
        assert ev.actor.team == "Team Vitality"
        assert ev.site == "B"
        assert (ev.pos_x, ev.pos_y) == (61.8, 394.6)
        assert ev.victim is None

    def test_round9_kill_sequence(self):
        events = self.data.round(9).events
        assert len(events) == 9
        pairs = [(e.actor.name, e.victim.name, e.cause) for e in events]
        assert pairs[0] == ("Chronicle", "lukxo", "Phantom")
        assert pairs[4] == ("erde", "Chronicle", "Vandal")
        assert pairs[8] == ("tkzin", "Sayonara", "Phantom")
        # Each kill removes one player from the alive snapshot.
        assert [len(e.alive) for e in events] == [9, 8, 7, 6, 5, 4, 3, 2, 1]

    def test_boom_marker_not_logged_row(self):
        round14 = self.data.round(14)
        assert round14.boom_at == 7
        boom = round14.events[7]
        assert boom.type is ReplayEventType.BOOM
        assert boom.derived is True
        assert boom.actor is None
        assert boom.site == "B"
        assert boom.clock == "1:16"  # clock of the event it precedes
        assert boom.seconds == 76
        assert (boom.pos_x, boom.pos_y) == (101.9, 447.6)  # spike plant position
        # The round ends on a detonation: the kill feed continues after it.
        assert round14.events[8].type is ReplayEventType.KILL
        assert round14.events[8].derived is False

    def test_boom_after_last_feed_row(self):
        boom = self.data.round(3).events[4]
        assert boom.type is ReplayEventType.BOOM
        assert boom.derived is True
        assert boom.clock == ""  # no following event to borrow the clock from
        assert boom.seconds is None
        assert boom.site == "B"

    def test_derived_resurrections(self):
        round12 = self.data.round(12)
        res = [e for e in round12.events if e.type is ReplayEventType.RESURRECT]
        assert len(res) == 1
        ev = res[0]
        assert ev.derived is True
        assert ev.actor.name == "DaviH"
        assert ev.actor.agent == "sova"
        assert ev.clock == "0:41"
        assert ev.seconds == 41
        assert ev.alive  # snapshot included
        round17 = self.data.round(17)
        res17 = [e for e in round17.events if e.type is ReplayEventType.RESURRECT]
        assert len(res17) == 1
        assert res17[0].actor.name == "tkzin"

    def test_event_type_totals(self):
        assert _type_counts(self.data) == {
            "kill": 125, "plant": 13, "defuse": 2, "boom": 3, "resurrect": 2,
        }

    def test_kill_causes_include_abilities(self):
        causes = {e.cause for rd in self.data.rounds for e in rd.events if e.type is ReplayEventType.KILL}
        assert "Sheriff" in causes
        assert any("Fury" in c for c in causes)  # Sova ult kill

    def test_full_names(self):
        assert ReplayEventType.KILL.full_name == "Kill"
        assert ReplayEventType.PLANT.full_name == "Planted"
        assert ReplayEventType.DEFUSE.full_name == "Defused"
        assert ReplayEventType.BOOM.full_name == "Spike detonated"
        assert ReplayEventType.RESURRECT.full_name == "Resurrected"


class TestUnplayedMap:
    """Game 283290 (Abyss, unplayed) must yield an empty timeline."""

    @property
    def data(self):
        return _parse(DIR_283288, 283290)

    def test_empty_replay_data(self):
        assert self.data.rounds == []
        assert self.data.num_rounds == 0
        assert self.data.team1 == ""
        assert self.data.team2 == ""


class TestLR3Revivals:
    """Game 283305 (100 Thieves vs G2) - Sage resurrects across the series."""

    @property
    def data(self):
        return _parse(DIR_283305, 283305)

    def test_top_level(self):
        assert self.data.team1 == "100 Thieves"
        assert self.data.team2 == "G2 Esports"
        assert self.data.num_rounds == 20

    def test_resurrection_events(self):
        for round_number, revived_name, revived_agent in (
            (4, "vora", "fade"),
            (8, "Timotino", "neon"),
            (18, "vora", "fade"),
        ):
            events = [e for e in self.data.round(round_number).events if e.type is ReplayEventType.RESURRECT]
            assert len(events) == 1
            assert events[0].derived is True
            assert events[0].actor.name == revived_name
            assert events[0].actor.agent == revived_agent

    def test_ult_kill_causes(self):
        causes = {e.cause for rd in self.data.rounds for e in rd.events if e.type is ReplayEventType.KILL}
        assert "Overdrive" in causes  # Neon ult
        assert "Tour de Force" in causes  # Chamber ult
        assert "Headhunter" in causes  # Chamber pistol

    def test_event_type_totals(self):
        assert _type_counts(self.data) == {
            "kill": 139, "plant": 13, "defuse": 4, "boom": 4, "resurrect": 3,
        }


class TestLBFRevivals:
    """Game 286701 (Team Vitality vs 100 Thieves)."""

    @property
    def data(self):
        return _parse(DIR_286701, 286701)

    def test_top_level(self):
        assert self.data.team1 == "Team Vitality"
        assert self.data.team2 == "100 Thieves"
        assert self.data.num_rounds == 23

    def test_double_resurrection(self):
        revived = [(rd.round_number, e.actor.name) for rd in self.data.rounds for e in rd.events if e.type is ReplayEventType.RESURRECT]
        assert revived == [(5, "Timotino"), (10, "Timotino")]

    def test_event_type_totals(self):
        assert _type_counts(self.data) == {
            "kill": 163, "plant": 14, "defuse": 3, "boom": 1, "resurrect": 2,
        }


class TestChampions2024GFClove:
    """Game 180437 (EDG vs Heretics) - Clove self-resurrects, ability kills."""

    @property
    def data(self):
        return _parse(DIR_180437, 180437)

    def test_top_level(self):
        assert self.data.team1 == "EDward Gaming"
        assert self.data.team2 == "Team Heretics"
        assert self.data.num_rounds == 22

    def test_clove_self_resurrect(self):
        revived = [
            (rd.round_number, e.actor.name, e.actor.agent, e.actor.team)
            for rd in self.data.rounds
            for e in rd.events
            if e.type is ReplayEventType.RESURRECT
        ]
        assert revived == [
            (10, "Smoggy", "clove", "EDward Gaming"),
            (20, "Smoggy", "clove", "EDward Gaming"),
        ]

    def test_ability_and_spike_kill_causes(self):
        causes = {e.cause for rd in self.data.rounds for e in rd.events if e.type is ReplayEventType.KILL}
        assert {"Not Dead Yet", "Showstopper", "Aftershock", "Nanoswarm", "Overdrive", "Spike"} <= causes

    def test_event_type_totals(self):
        assert _type_counts(self.data) == {
            "kill": 160, "plant": 16, "defuse": 3, "boom": 2, "resurrect": 2,
        }
