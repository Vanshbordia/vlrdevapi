Series API
==========

The series module provides detailed match information including map picks/bans, player statistics, and round-by-round data.

Overview
--------

Get in-depth match analytics including series info, map picks and bans, detailed player statistics, and round results.

.. automodule:: vlrdevapi.series
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

info
~~~~

.. autofunction:: vlrdevapi.series.info
   :noindex:

matches
~~~~~~~

.. autofunction:: vlrdevapi.series.matches
   :noindex:

performance
~~~~~~~~~~~

.. autofunction:: vlrdevapi.series.performance
   :noindex:

Data Models
-----------

TeamInfo
~~~~~~~~

.. autoclass:: vlrdevapi.series.TeamInfo
   :members:
   :undoc-members:

MapAction
~~~~~~~~~

.. autoclass:: vlrdevapi.series.MapAction
   :members:
   :undoc-members:

Info
~~~~

.. autoclass:: vlrdevapi.series.Info
   :members:
   :undoc-members:

PlayerStats
~~~~~~~~~~~

.. autoclass:: vlrdevapi.series.PlayerStats
   :members:
   :undoc-members:

MapTeamScore
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.series.MapTeamScore
   :members:
   :undoc-members:

RoundResult
~~~~~~~~~~~

.. autoclass:: vlrdevapi.series.RoundResult
   :members:
   :undoc-members:

MapPlayers
~~~~~~~~~~

.. autoclass:: vlrdevapi.series.MapPlayers
   :members:
   :undoc-members:

MultiKillDetail
~~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.series.MultiKillDetail
   :members:
   :undoc-members:

ClutchDetail
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.series.ClutchDetail
   :members:
   :undoc-members:

PlayerPerformance
~~~~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.series.PlayerPerformance
   :members:
   :undoc-members:

Usage Examples
--------------

Get Series Information
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get match/series info
   info = vlr.series.info(match_id=530935)
   
   print(f"{info.teams[0].name} vs {info.teams[1].name}")
   print(f"Score: {info.score[0]}-{info.score[1]}")
   print(f"Event: {info.event} - {info.event_phase}")
   print(f"Format: {info.best_of}")
   print(f"Date: {info.date}")

Map Picks and Bans
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   info = vlr.series.info(match_id=530935)
   
   # Show map picks
   print("Map Picks:")
   for pick in info.picks:
       print(f"  {pick.team} picked {pick.map}")
   
   # Show map bans
   print("\nMap Bans:")
   for ban in info.bans:
       print(f"  {ban.team} banned {ban.map}")

Get Detailed Map Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get per-map statistics
   maps = vlr.series.matches(series_id=530935)
   
   for i, map_data in enumerate(maps, 1):
       print(f"\nMap {i}: {map_data.map_name}")
       
       # Team scores
       if map_data.teams:
           team1, team2 = map_data.teams
           print(f"{team1.name} {team1.score} - {team2.score} {team2.name}")
           winner = team1.name if team1.is_winner else team2.name
           print(f"Winner: {winner}")
       
       # Player statistics
       print("\nPlayer Stats:")
       for player in map_data.players:
           print(f"  {player.name} ({player.team_short})")
           print(f"    K/D/A: {player.k}/{player.d}/{player.a}")
           print(f"    Rating: {player.r}, ACS: {player.acs}")
           print(f"    ADR: {player.adr}, KAST: {player.kast}")

Round-by-Round Results
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   maps = vlr.series.matches(series_id=530935)
   
   for map_data in maps:
       if map_data.rounds:
           print(f"\n{map_data.map_name} - Round Results:")
           for round_result in map_data.rounds:
               print(f"  Round {round_result.number}: {round_result.winner_team_short} ({round_result.method})")
               if round_result.score:
                   print(f"    Score: {round_result.score[0]}-{round_result.score[1]}")

Top Performers
~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   maps = vlr.series.matches(series_id=530935)

   for map_data in maps:
       # Sort by ACS
       sorted_players = sorted(
           map_data.players,
           key=lambda p: p.acs or 0,
           reverse=True
       )

       print(f"\n{map_data.map_name} - Top 3 Performers:")
       for player in sorted_players[:3]:
           print(f"  {player.name}: {player.acs} ACS, {player.k}/{player.d}/{player.a}")

Match Performance Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get performance statistics for a series
   perf = vlr.series.performance(series_id=542210)

   for game in perf:
       print(f"\nMap: {game.map_name}")
       for player in game.player_performances:
           print(f"  {player.name} ({player.team_short})")
           print(f"    2Ks: {player.multi_2k}, 3Ks: {player.multi_3k}, 4Ks: {player.multi_4k}, 5Ks: {player.multi_5k}")
           print(f"    1v1: {player.clutch_1v1}, 1v2: {player.clutch_1v2}, 1v3: {player.clutch_1v3}")
           print(f"    ECON: {player.econ}, Plants: {player.plants}, Defuses: {player.defuses}")

           # Detailed performance information
           if player.multi_2k_details:
               print(f"    2K Details: {len(player.multi_2k_details)} events")
               for detail in player.multi_2k_details:
                   print(f"      Round {detail.round_number}: {', '.join(detail.players_killed)}")
           if player.clutch_1v2_details:
               print(f"    1v2 Details: {len(player.clutch_1v2_details)} events")
               for detail in player.clutch_1v2_details:
                   print(f"      Round {detail.round_number}: {', '.join(detail.players_killed)}")

See more examples: :doc:`../examples`
