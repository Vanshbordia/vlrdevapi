Quick Start Guide
=================

Welcome to vlrdevapi, the Python library for VLR.gg Valorant esports data access.

This guide covers the essential operations for accessing Valorant tournament data, match information, player statistics, and more. Whether you're building a VCT tournament tracker, creating a Discord bot for match notifications, developing betting prediction models, analyzing player performance across agents and maps, or conducting research on competitive gaming, this library provides all the tools you need to extract and work with Valorant esports data from VLR.gg.

Basic Usage
-----------

Import the library
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

Working with Events
~~~~~~~~~~~~~~~~~~~

List events with filters:

.. code-block:: python

   # List all VCT events
   events = vlr.events.list_events(tier="vct")
   
   # Filter by status
   ongoing_events = vlr.events.list_events(tier="vct", status="ongoing")
   
   # Filter by region
   na_events = vlr.events.list_events(tier="vct", region="na")
   
   # Print event details
   for event in events:
       print(f"{event.name}")
       print(f"  Status: {event.status}")
       print(f"  Prize: {event.prize}")
       print(f"  Dates: {event.start_date} to {event.end_date}")

Get detailed event information:

.. code-block:: python

   # Get event header/info
   info = vlr.events.info(event_id=2498)
   print(f"{info.name}")
   print(f"Prize: {info.prize}")
   print(f"Location: {info.location}")

Working with Teams
~~~~~~~~~~~~~~~~~~

Get team information and statistics:

.. code-block:: python

   # Get team information
   team_info = vlr.teams.info(team_id=799)
   print(f"{team_info.name} ({team_info.tag})")
   print(f"Country: {team_info.country}")
   print(f"Active: {team_info.is_active}")
   
   # Get team roster
   roster = vlr.teams.roster(team_id=799)
   for member in roster:
       print(f"{member.ign} - {member.name}")
   
   # Get team matches with pagination
   upcoming = vlr.teams.upcoming_matches(team_id=799, count=10)
   completed = vlr.teams.completed_matches(team_id=799, count=20)
   
   # Get event placements
   placements = vlr.teams.placements(team_id=799)
   for placement in placements[:5]:
       print(f"{placement.event_name} ({placement.year})")
       for detail in placement.placements:
           print(f"  {detail.series}: {detail.place} - {detail.prize_money}")
   
   # Get event matches
   matches = vlr.events.matches(event_id=2498)
   for match in matches:
       team1, team2 = match.teams
       print(f"{team1.name} vs {team2.name}")
   
   # Get event standings
   standings = vlr.events.standings(event_id=2498)
   for entry in standings.entries:
       print(f"{entry.place}. {entry.team_name} - {entry.prize}")

Working with Matches
~~~~~~~~~~~~~~~~~~~~

Get upcoming, live, and completed matches:

.. code-block:: python

   # Upcoming matches
   upcoming = vlr.matches.upcoming(limit=10)
   for match in upcoming:
       print(f"{match.teams[0]} vs {match.teams[1]}")
       print(f"  Event: {match.event}")
       print(f"  Time: {match.time}")
   
   # Live matches
   live = vlr.matches.live()
   for match in live:
       print(f"LIVE: {match.teams[0]} vs {match.teams[1]}")
   
   # Completed matches
   completed = vlr.matches.completed(limit=10)
   for match in completed:
       print(f"{match.teams[0]} vs {match.teams[1]}")
       print(f"  Score: {match.score}")
       print(f"  Event: {match.event}")

Working with Players
~~~~~~~~~~~~~~~~~~~~

Get player profiles and statistics:

.. code-block:: python

   # Player profile
   profile = vlr.players.profile(player_id=4164)
   print(f"Handle: {profile.handle}")
   print(f"Real Name: {profile.real_name}")
   print(f"Country: {profile.country}")
   
   # Current teams
   for team in profile.current_teams:
       print(f"  {team.name} - {team.role}")
   
   # Player match history
   matches = vlr.players.matches(player_id=4164, limit=20)
   for match in matches:
       print(f"{match.player_team.name} vs {match.opponent_team.name}")
       print(f"  Result: {match.result}")
       print(f"  Score: {match.player_score}-{match.opponent_score}")
   
   # Agent statistics
   stats = vlr.players.agent_stats(player_id=4164, timespan="60d")
   for stat in stats:
       print(f"{stat.agent}:")
       print(f"  Rating: {stat.rating}")
       print(f"  ACS: {stat.acs}")
       print(f"  K/D: {stat.kd}")
       print(f"  Usage: {stat.usage_percent * 100:.1f}%")

Working with Series
~~~~~~~~~~~~~~~~~~~

Get detailed match information:

.. code-block:: python

   # Series information
   info = vlr.series.info(match_id=530935)
   print(f"{info.teams[0].name} vs {info.teams[1].name}")
   print(f"Score: {info.score[0]}-{info.score[1]}")
   print(f"Event: {info.event} - {info.event_phase}")
   print(f"Best of: {info.best_of}")
   
   # Map picks and bans
   for pick in info.picks:
       print(f"{pick.team} picked {pick.map}")
   for ban in info.bans:
       print(f"{ban.team} banned {ban.map}")
   
   # Detailed map statistics
   maps = vlr.series.matches(series_id=530935)
   for map_data in maps:
       print(f"\nMap: {map_data.map_name}")
       
       # Team scores
       if map_data.teams:
           team1, team2 = map_data.teams
           print(f"{team1.name} {team1.score} - {team2.score} {team2.name}")
       
       # Player statistics
       for player in map_data.players:
           print(f"  {player.name}: {player.k}/{player.d}/{player.a}")
           print(f"    Rating: {player.r}, ACS: {player.acs}")

Error Handling
--------------

Handle network errors and rate limiting:

.. code-block:: python

   from vlrdevapi.exceptions import NetworkError, RateLimitError
   
   try:
       events = vlr.events.list_events()
   except RateLimitError:
       print("Rate limited by VLR.gg. Please wait before retrying.")
   except NetworkError as e:
       print(f"Network error occurred: {e}")

Cache Management
----------------

Clear cache for fresh data:

.. code-block:: python

   # Clear cache to force fresh data fetch
   vlr.fetcher.clear_cache()
   
   # Now fetch fresh data
   events = vlr.events.list_events()

Close connections on application shutdown:

.. code-block:: python

   # At application exit
   vlr.fetcher.close_connections()

Next Steps
----------

- Explore the :doc:`examples` for more detailed use cases
- Read the :doc:`api/events` for complete API documentation
- Learn about :doc:`performance` optimizations
