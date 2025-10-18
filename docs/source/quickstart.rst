Quick Start Guide
=================

This guide will get you started with vlrdevapi in minutes.

Installation
------------

First, install the library:

.. code-block:: bash

   pip install vlrdevapi

Requires Python 3.11 or higher.

Basic Usage
-----------

Import the Library
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

Search for Anything
~~~~~~~~~~~~~~~~~~~

The search module is the easiest way to find players, teams, events, or series:

.. code-block:: python

   import vlrdevapi as vlr
   # Search everything
   results = vlr.search.search("nrg")
   print(f"Found {results.total_results} results")
   
   # Access different result types
   for team in results.teams:
       print(f"Team: {team.name} - {team.country}")
   
   for player in results.players:
       print(f"Player: {player.ign} - {player.country}")

Type-specific searches (set ``enrich=False`` for the fastest raw results):

.. code-block:: python

   import vlrdevapi as vlr
   # Search only players
   players = vlr.search.search_players("tenz")
   
   # Search only teams
   teams = vlr.search.search_teams("sentinels")
   
   # Search only events
   events = vlr.search.search_events("champions")

Get Match Schedules
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Upcoming matches
   upcoming = vlr.matches.upcoming(limit=10)
   for match in upcoming:
       print(f"{match.team1.name} vs {match.team2.name}")
       print(f"Event: {match.event}")
       print(f"Countries: {match.team1.country} vs {match.team2.country}")
   
   # Live matches
   live = vlr.matches.live()
   for match in live:
       print(f"LIVE: {match.team1.name} vs {match.team2.name}")
   
   # Completed matches
   completed = vlr.matches.completed(limit=10)
   for match in completed:
       score = f"{match.team1.score}-{match.team2.score}"
       print(f"{match.team1.name} vs {match.team2.name}: {score}")

Player Information
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Get player profile
   profile = vlr.players.profile(player_id=4164)
   print(f"{profile.handle} ({profile.real_name})")
   print(f"Country: {profile.country}")
   
   # Get player stats
   stats = vlr.players.agent_stats(player_id=4164, timespan="60d")
   for stat in stats[:3]:
       print(f"{stat.agent}: {stat.rating} rating, {stat.acs} ACS")
   
   # Get match history
   matches = vlr.players.matches(player_id=4164, limit=10)
   for match in matches:
       print(f"{match.event} - {match.stage} {match.phase}: {match.result}")

Team Information
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Get team info
   team = vlr.teams.info(team_id=1034)
   print(f"{team.name} ({team.tag}) - {team.country}")
   
   # Get roster
   roster = vlr.teams.roster(team_id=1034)
   for member in roster:
       print(f"{member.ign} - {member.role}")
   
   # Get team matches
   upcoming = vlr.teams.upcoming_matches(team_id=1034, limit=5)
   completed = vlr.teams.completed_matches(team_id=1034, limit=10)

Event Information
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # List events
   events = vlr.events.list_events(tier="vct", status="ongoing")
   
   # Get event details
   info = vlr.events.info(event_id=2498)
   print(f"{info.name} - {info.prize}")
   
   # Get event matches
   matches = vlr.events.matches(event_id=2498)

Match Details
~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Get detailed match info
   info = vlr.series.info(match_id=530935)
   print(f"{info.teams[0].name} vs {info.teams[1].name}")
   print(f"Score: {info.score[0]}-{info.score[1]}")
   
   # Get map statistics
   maps = vlr.series.matches(series_id=530935)
   for map_data in maps:
       print(f"Map: {map_data.map_name}")

Common Patterns
---------------

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import NetworkError, RateLimitError
   
   try:
       results = vlr.search.search("nrg")
   except RateLimitError:
       print("Rate limited. Please wait.")
   except NetworkError as e:
       print(f"Network error: {e}")

Pagination
~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Get specific page
   page1 = vlr.matches.completed(page=1)
   page2 = vlr.matches.completed(page=2)

Caching
~~~~~~~

``vlr.fetcher`` caches responses in process. Clear it when you need fresh HTML:

.. code-block:: python

   import vlrdevapi as vlr
   vlr.fetcher.clear_cache()

Async Fetching
~~~~~~~~~~~~~~

The fetcher also exposes async helpers if you are running inside an async application:

.. code-block:: python

   import asyncio
   from vlrdevapi import fetcher

   async def load_match_async(match_url: str) -> str:
       html = await fetcher.fetch_html_async(match_url)
       return html

   asyncio.run(load_match_async("https://www.vlr.gg"))

Filtering
~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Filter events by tier and status
   vct_events = vlr.events.list_events(tier="vct", status="ongoing")
   
   # Filter player stats by timespan
   stats = vlr.players.agent_stats(player_id=4164, timespan="30d")

Next Steps
----------

- See :doc:`examples` for practical use cases
- Browse :doc:`api/search` and other API references
- Learn about :doc:`performance` optimizations
