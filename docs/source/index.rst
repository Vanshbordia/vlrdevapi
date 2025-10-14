vlrdevapi Documentation
=======================

**Python library for VLR.gg Valorant esports data**

Welcome to vlrdevapi, a comprehensive Python library for accessing Valorant esports data from VLR.gg. This library provides type-safe, production-ready access to tournament information, match schedules, player statistics, team data, and more.

Overview
--------

vlrdevapi enables developers to:

- Access VCT (Valorant Champions Tour) tournament data
- Track match schedules and live results
- Analyze player performance and statistics
- Monitor team rosters and placements
- Search across players, teams, events, and series

Key Features
~~~~~~~~~~~~

- **Complete Coverage**: Events, matches, players, teams, series, and search
- **Type-Safe**: Full Pydantic models with automatic validation
- **Production-Ready**: Error handling, retry logic, and rate limiting
- **Easy to Use**: Simple, intuitive API design
- **Well-Tested**: Comprehensive test suite with real HTML fixtures

Quick Example
-------------

.. code-block:: python

   import vlrdevapi as vlr

   # Search for anything
   results = vlr.search.search("nrg")
   print(f"Found {results.total_results} results")

   # Get upcoming matches
   matches = vlr.matches.upcoming(limit=5)
   for match in matches:
       print(f"{match.teams[0]} vs {match.teams[1]}")

   # Player profile
   profile = vlr.players.profile(player_id=4164)
   print(f"{profile.handle} - {profile.country}")

Installation
------------

.. code-block:: bash

   pip install vlrdevapi

Requires Python 3.11 or higher.

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/search
   api/matches
   api/players
   api/teams
   api/events
   api/series
   api/exceptions

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   performance
   contributing

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

