Usage Examples
==============

This page provides practical examples for common use cases.

Example 1: Track Tournament Progress
-------------------------------------

Monitor an ongoing tournament and display match results:

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

Example 2: Player Performance Analysis
---------------------------------------

Analyze a player's recent performance across different agents:

.. code-block:: python

   import vlrdevapi as vlr
   
   def analyze_player(player_id, timespan="60d"):
       # Get profile
       profile = vlr.players.profile(player_id=player_id)
       print(f"Player: {profile.handle} ({profile.real_name})")
       print(f"Country: {profile.country}")
       print()
       
       # Get agent stats
       stats = vlr.players.agent_stats(player_id=player_id, timespan=timespan)
       
       # Sort by usage
       stats_sorted = sorted(stats, key=lambda s: s.usage_count or 0, reverse=True)
       
       print(f"Agent Performance (Past {timespan}):")
       print(f"{'Agent':<15} {'Games':<8} {'Rating':<8} {'ACS':<8} {'K/D':<8}")
       print("-" * 55)
       
       for stat in stats_sorted[:5]:
           if stat.agent and stat.agent != "All":
               games = stat.usage_count or 0
               rating = f"{stat.rating:.2f}" if stat.rating else "N/A"
               acs = f"{stat.acs:.0f}" if stat.acs else "N/A"
               kd = f"{stat.kd:.2f}" if stat.kd else "N/A"
               print(f"{stat.agent:<15} {games:<8} {rating:<8} {acs:<8} {kd:<8}")
       
       # Get recent matches
       matches = vlr.players.matches(player_id=player_id, limit=10)
       
       wins = sum(1 for m in matches if m.result == "win")
       losses = sum(1 for m in matches if m.result == "loss")
       
       print()
       print(f"Recent Match Record: {wins}W - {losses}L")
   
   analyze_player(player_id=4164)

Example 3: Match Deep Dive
---------------------------

Get detailed statistics for a specific match:

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

Example 4: Live Match Monitor
------------------------------

Monitor live matches and display updates:

.. code-block:: python

   import vlrdevapi as vlr
   import time
   
   def monitor_live_matches(refresh_interval=60):
       print("Live Match Monitor")
       print("=" * 50)
       
       while True:
           # Clear cache to get fresh data
           vlr.fetcher.clear_cache()
           
           # Get live matches
           live_matches = vlr.matches.live()
           
           if not live_matches:
               print("No live matches at the moment.")
           else:
               print(f"\n{len(live_matches)} live match(es):")
               for match in live_matches:
                   print(f"\n  {match.teams[0]} vs {match.teams[1]}")
                   print(f"  Event: {match.event}")
                   if match.score:
                       print(f"  Score: {match.score}")
           
           print(f"\nRefreshing in {refresh_interval} seconds...")
           time.sleep(refresh_interval)
   
   # Run for a limited time in this example
   # monitor_live_matches(refresh_interval=60)

Example 5: Team Comparison
---------------------------

Compare two teams based on recent match results:

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

Example 6: Export Data to CSV
------------------------------

Export event data to a CSV file:

.. code-block:: python

   import vlrdevapi as vlr
   import csv
   
   def export_event_matches_to_csv(event_id, filename="matches.csv"):
       # Get event info and matches
       info = vlr.events.info(event_id=event_id)
       matches = vlr.events.matches(event_id=event_id)
       
       # Write to CSV
       with open(filename, 'w', newline='', encoding='utf-8') as f:
           writer = csv.writer(f)
           
           # Header
           writer.writerow([
               'Match ID', 'Team 1', 'Team 2', 'Score 1', 'Score 2',
               'Winner', 'Stage', 'Status', 'Date'
           ])
           
           # Data rows
           for match in matches:
               team1, team2 = match.teams
               winner = team1.name if team1.is_winner else (team2.name if team2.is_winner else "TBD")
               
               writer.writerow([
                   match.match_id,
                   team1.name,
                   team2.name,
                   team1.score or '',
                   team2.score or '',
                   winner,
                   match.stage or '',
                   match.status,
                   match.date or ''
               ])
       
       print(f"Exported {len(matches)} matches to {filename}")
   
   export_event_matches_to_csv(event_id=2498)

These examples demonstrate common patterns and use cases. Adapt them to your specific needs.
