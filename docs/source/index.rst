vlrdevapi Documentation
=======================

**Python library for VLR.gg Valorant esports data**

Welcome to vlrdevapi, a comprehensive Python library for accessing Valorant esports data from VLR.gg. This library provides type-safe, production-ready access to tournament information, match schedules, player statistics, team data, and more via a modern `httpx` networking layer with HTTP/2 support.

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

- **Complete Coverage**: Events, matches, players, teams, series, and search modules
- **Type-Safe Models**: Frozen Python dataclasses with rich type hints
- **Modern Fetcher**: Shared `httpx` clients with retry logic, HTTP/2 multiplexing, Brotli/gzip decoding, and in-process caching
- **Ergonomic API**: Pythonic entrypoints under ``vlr`` with practical examples
- **Well-Tested**: HTML fixtures and test suite for regression safety

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
       print(f"{match.team1.name} vs {match.team2.name}")

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
   performance
   rate-limiting

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
   api/models

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   contributing

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

