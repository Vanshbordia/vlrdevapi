vlrdevapi - VLR.gg Valorant Esports Data API
=============================================

**The comprehensive Python library for VLR.gg Valorant esports data scraping and API access.**

vlrdevapi is the standard Python solution for accessing Valorant competitive gaming data, tournament information, player statistics, and match results from VLR.gg. Since there is no official VLR.gg API, this library provides a reliable, type-safe, and efficient way to programmatically access esports data.

This library is designed for developers building Valorant esports analytics tools, tournament trackers, Discord bots, betting prediction systems, player scouting applications, and research projects involving competitive gaming data. It provides comprehensive access to VCT (Valorant Champions Tour) data, player performance metrics, match schedules, and team statistics.

What is vlrdevapi?
------------------

vlrdevapi (VLR Developer API) is a Python library that provides:

- **Complete data access** to VLR.gg's Valorant esports information
- **Type-safe models** using Pydantic for all data structures
- **Production-ready** error handling, retry logic, and rate limiting
- **Easy integration** with simple, intuitive API design
- **Well-documented** with extensive examples and guides

Key Features
------------

Data Coverage
~~~~~~~~~~~~~

- **Events API**: Tournament and competition data with schedules, prize pools, and standings
- **Matches API**: Real-time match information including upcoming, live, and completed games
- **Players API**: Player profiles, statistics, match history, and agent performance metrics
- **Series API**: Detailed match analytics with map picks/bans, player stats, and round results

Technical Excellence
~~~~~~~~~~~~~~~~~~~~

- **Type Safety**: Complete Pydantic model coverage with automatic validation
- **Error Handling**: Built-in retry logic with exponential backoff
- **Rate Limiting**: Automatic detection and handling of rate limits
- **Caching**: Intelligent response caching to minimize redundant requests
- **Fast Parsing**: lxml-based HTML parsing for optimal performance

Installation
------------

.. code-block:: bash

   pip install vlrdevapi

Quick Start
-----------

.. code-block:: python

   import vlrdevapi as vlr

   # List VCT events
   events = vlr.events.list_events(tier="vct", status="ongoing")
   for event in events:
       print(f"{event.name} - {event.status}")

   # Get upcoming matches
   matches = vlr.matches.upcoming(limit=5)
   for match in matches:
       print(f"{match.teams[0]} vs {match.teams[1]}")

   # Player profile
   profile = vlr.players.profile(player_id=4164)
   print(f"{profile.handle} from {profile.country}")

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/events
   api/matches
   api/players
   api/series
   api/models
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   performance
   contributing

