Usage Examples
==============

This page provides practical examples for common use cases with vlrdevapi.

Search Examples
---------------

Search Across All Types
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   results = vlr.search.search("nrg")
   print(f"Found {results.total_results} results")

   for team in results.teams:
       status = "inactive" if team.is_inactive else "active"
       print(f"Team: {team.name} ({status}) - {team.country}")

   for player in results.players:
       rn = f" ({player.real_name})" if player.real_name else ""
       print(f"Player: {player.ign}{rn} - {player.country}")

Type-Specific Searches
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Search only players
   players = vlr.search.search_players("tenz")
   
   # Search only teams
   teams = vlr.search.search_teams("sentinels")
   
   # Search only events
   events = vlr.search.search_events("champions")

Match Tracking Examples
-----------------------

Track Tournament Progress
~~~~~~~~~~~~~~~~~~~~~~~~~

Monitor an ongoing tournament:

.. code-block:: python

   import vlrdevapi as vlr
   
   def track_tournament(event_id):
       # Get event info
       info = vlr.events.info(event_id=event_id)
       print(f"Tournament: {info.name}")
       print(f"Prize Pool: {info.prize}")
       print(f"Location: {info.location}")
       print()
       
       # Get all matches
       matches = vlr.events.matches(event_id=event_id)
       
       # Separate by status
       completed = [m for m in matches if m.status == "completed"]
       upcoming = [m for m in matches if m.status == "upcoming"]
       live = [m for m in matches if m.status == "live"]
       
       print(f"Completed: {len(completed)}")
       print(f"Upcoming: {len(upcoming)}")
       print(f"Live: {len(live)}")
       print()
       
       # Show recent results
       print("Recent Results:")
       for match in completed[:5]:
           team1, team2 = match.teams
           print(f"  {team1.name} vs {team2.name}")
           if team1.score is not None and team2.score is not None:
               winner = team1.name if team1.is_winner else team2.name
               print(f"    Winner: {winner} ({team1.score}-{team2.score})")
   
   track_tournament(event_id=2498)

Live Match Monitor
~~~~~~~~~~~~~~~~~~

Monitor live matches:

.. code-block:: python

   import vlrdevapi as vlr
   import time
   
   def monitor_live_matches(refresh_interval=60):
       while True:
           vlr.fetcher.clear_cache()
           live_matches = vlr.matches.live()
           
           if not live_matches:
               print("No live matches")
           else:
               print(f"{len(live_matches)} live match(es):")
               for match in live_matches:
                   print(f"  {match.teams[0]} vs {match.teams[1]}")
                   print(f"  Event: {match.event}")
           
           time.sleep(refresh_interval)

Player Analysis Examples
------------------------

Player Performance Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Analyze player performance across agents:

.. code-block:: python

   import vlrdevapi as vlr
   
   def analyze_player(player_id, timespan="60d"):
       # Get profile
       profile = vlr.players.profile(player_id=player_id)
       print(f"Player: {profile.handle} ({profile.real_name})")
       print(f"Country: {profile.country}")
       
       # Get agent stats
       stats = vlr.players.agent_stats(player_id=player_id, timespan=timespan)
       stats_sorted = sorted(stats, key=lambda s: s.usage_count or 0, reverse=True)
       
       print(f"\nTop Agents (Past {timespan}):")
       for stat in stats_sorted[:5]:
           if stat.agent and stat.agent != "All":
               print(f"{stat.agent}: {stat.rating:.2f} rating, {stat.acs:.0f} ACS")
       
       # Get recent match record
       matches = vlr.players.matches(player_id=player_id, limit=10)
       wins = sum(1 for m in matches if m.result == "win")
       losses = sum(1 for m in matches if m.result == "loss")
       print(f"\nRecent Record: {wins}W - {losses}L")
   
   analyze_player(player_id=4164)

Match Analysis Examples
-----------------------

Match Deep Dive
~~~~~~~~~~~~~~~

Get detailed statistics for a match:

.. code-block:: python

   import vlrdevapi as vlr
   
   def match_deep_dive(match_id):
       # Get series info
       info = vlr.series.info(match_id=match_id)
       
       print(f"Match: {info.teams[0].name} vs {info.teams[1].name}")
       print(f"Event: {info.event} - {info.event_phase}")
       print(f"Final Score: {info.score[0]}-{info.score[1]}")
       print(f"Format: {info.best_of}")
       print()
       
       # Show picks and bans
       if info.picks:
           print("Map Picks:")
           for pick in info.picks:
               print(f"  {pick.team} picked {pick.map}")
       
       if info.bans:
           print("\nMap Bans:")
           for ban in info.bans:
               print(f"  {ban.team} banned {ban.map}")
       
       print()
       
       # Get detailed map stats
       maps = vlr.series.matches(series_id=match_id)
       
       for i, map_data in enumerate(maps, 1):
           print(f"\nMap {i}: {map_data.map_name}")
           
           if map_data.teams:
               team1, team2 = map_data.teams
               winner = team1.name if team1.is_winner else team2.name
               print(f"  {team1.name} {team1.score} - {team2.score} {team2.name}")
               print(f"  Winner: {winner}")
           
           # Top performers
           if map_data.players:
               sorted_players = sorted(
                   map_data.players,
                   key=lambda p: p.acs or 0,
                   reverse=True
               )
               
               print(f"\n  Top Performers:")
               for player in sorted_players[:3]:
                   print(f"    {player.name}: {player.acs} ACS, {player.k}/{player.d}/{player.a}")
   
   match_deep_dive(match_id=530935)

Team Analysis Examples
----------------------

Team Comparison
~~~~~~~~~~~~~~~

Compare two teams:

.. code-block:: python

   import vlrdevapi as vlr
   from collections import defaultdict
   
   def compare_teams_from_event(event_id, team1_name, team2_name):
       # Get event matches
       matches = vlr.events.matches(event_id=event_id)
       
       team_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "maps_won": 0, "maps_lost": 0})
       
       for match in matches:
           if match.status != "completed":
               continue
           
           t1, t2 = match.teams
           
           # Check if our teams are in this match
           for team_name in [team1_name, team2_name]:
               if team_name.lower() in t1.name.lower():
                   if t1.is_winner:
                       team_stats[team_name]["wins"] += 1
                       team_stats[team_name]["maps_won"] += t1.score or 0
                       team_stats[team_name]["maps_lost"] += t2.score or 0
                   else:
                       team_stats[team_name]["losses"] += 1
                       team_stats[team_name]["maps_won"] += t1.score or 0
                       team_stats[team_name]["maps_lost"] += t2.score or 0
               
               elif team_name.lower() in t2.name.lower():
                   if t2.is_winner:
                       team_stats[team_name]["wins"] += 1
                       team_stats[team_name]["maps_won"] += t2.score or 0
                       team_stats[team_name]["maps_lost"] += t1.score or 0
                   else:
                       team_stats[team_name]["losses"] += 1
                       team_stats[team_name]["maps_won"] += t2.score or 0
                       team_stats[team_name]["maps_lost"] += t1.score or 0
       
       print(f"Team Comparison for Event {event_id}")
       print("=" * 50)
       
       for team_name in [team1_name, team2_name]:
           stats = team_stats[team_name]
           print(f"\n{team_name}:")
           print(f"  Match Record: {stats['wins']}W - {stats['losses']}L")
           print(f"  Map Record: {stats['maps_won']}W - {stats['maps_lost']}L")
           
           if stats['wins'] + stats['losses'] > 0:
               win_rate = stats['wins'] / (stats['wins'] + stats['losses']) * 100
               print(f"  Win Rate: {win_rate:.1f}%")
   
   compare_teams_from_event(event_id=2498, team1_name="NRG", team2_name="FNATIC")

Team Analysis and Tracking
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track team performance:

.. code-block:: python

   import vlrdevapi as vlr
   
   def analyze_team(team_id):
       # Get team information
       info = vlr.teams.info(team_id=team_id)
       print(f"Team: {info.name} ({info.tag})")
       print(f"Country: {info.country}")
       print(f"Active: {info.is_active}")
       print()
       
       # Get current roster
       roster = vlr.teams.roster(team_id=team_id)
       print(f"Current Roster ({len(roster)} players):")
       for member in roster:
           print(f"  {member.ign} - {member.name}")
           if member.role:
               print(f"    Role: {member.role}")
       print()
       
       # Get recent match results
       completed = vlr.teams.completed_matches(team_id=team_id, count=5)
       print("Last 5 Matches:")
       for match in completed:
           result = f"{match.score_team1}-{match.score_team2}"
           print(f"  {match.team1_name} vs {match.team2_name}: {result}")
           print(f"    {match.tournament_name}")
       print()
       
       # Get upcoming matches
       upcoming = vlr.teams.upcoming_matches(team_id=team_id, count=3)
       print(f"Next {len(upcoming)} Matches:")
       for match in upcoming:
           print(f"  {match.team1_name} vs {match.team2_name}")
           print(f"    {match.tournament_name} - {match.date}")
       print()
       
       # Get tournament placements
       placements = vlr.teams.placements(team_id=team_id)
       print(f"Tournament History ({len(placements)} events):")
       for placement in placements[:5]:  # Show top 5
           print(f"\n  {placement.event_name} ({placement.year})")
           for detail in placement.placements:
               print(f"    {detail.series}: {detail.place} - {detail.prize_money}")
   
   analyze_team(team_id=799)

Team Roster History and Transactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Track team roster changes over time:

.. code-block:: python

   import vlrdevapi as vlr
   
   def roster_analysis(team_id):
       # Get all previous players with status
       players = vlr.teams.previous_players(team_id=team_id)
       
       # Group by status
       active = [p for p in players if p.status == "Active"]
       left = [p for p in players if p.status == "Left"]
       inactive = [p for p in players if p.status == "Inactive"]
       
       print(f"Roster Status Summary:")
       print(f"  Active: {len(active)}")
       print(f"  Left: {len(left)}")
       print(f"  Inactive: {len(inactive)}")
       print()
       
       # Show active players
       print("Current Active Players:")
       for player in active:
           print(f"  {player.ign} ({player.position})")
           print(f"    Joined: {player.join_date}")
           print(f"    Country: {player.country}")
       print()
       
       # Show recent departures
       print("Recent Departures:")
       for player in left[:5]:
           print(f"  {player.ign} ({player.position})")
           print(f"    Joined: {player.join_date}, Left: {player.leave_date}")
       print()
       
       # Get raw transactions
       txns = vlr.teams.transactions(team_id=team_id)
       
       # Analyze transaction patterns
       joins = [t for t in txns if t.action == "join"]
       leaves = [t for t in txns if t.action == "leave"]
       
       print(f"Transaction Summary:")
       print(f"  Total Joins: {len(joins)}")
       print(f"  Total Leaves: {len(leaves)}")
       print()
       
       # Show recent transactions
       print("Recent Transactions:")
       for txn in txns[:10]:
           print(f"  {txn.date}: {txn.ign} - {txn.action} ({txn.position})")
   
   roster_analysis(team_id=1034)

Data Export Examples
--------------------

Export to CSV
~~~~~~~~~~~~~

Export event data to CSV:

.. code-block:: python

   import vlrdevapi as vlr
   import csv
   
   def export_event_matches(event_id, filename="matches.csv"):
       matches = vlr.events.matches(event_id=event_id)
       
       with open(filename, 'w', newline='', encoding='utf-8') as f:
           writer = csv.writer(f)
           writer.writerow(['Team 1', 'Team 2', 'Score', 'Status'])
           
           for match in matches:
               team1, team2 = match.teams
               score = f"{team1.score}-{team2.score}" if team1.score else "TBD"
               writer.writerow([team1.name, team2.name, score, match.status])
       
       print(f"Exported {len(matches)} matches")
   
   export_event_matches(event_id=2498)

These examples demonstrate common patterns. Adapt them to your needs.
