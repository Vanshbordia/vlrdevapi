Search API
==========

The search module provides a unified interface to search VLR.gg for players, teams, events, and series.

Overview
--------

The search module is the easiest way to find anything on VLR.gg. It searches across all entity types and enriches results with additional data like country information.

.. automodule:: vlrdevapi.search
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

search
~~~~~~

Search across all types (players, teams, events, series).

.. autofunction:: vlrdevapi.search.search
   :noindex:

search_players
~~~~~~~~~~~~~~

Search for players only.

.. autofunction:: vlrdevapi.search.search_players
   :noindex:

search_teams
~~~~~~~~~~~~

Search for teams only.

.. autofunction:: vlrdevapi.search.search_teams
   :noindex:

search_events
~~~~~~~~~~~~~

Search for events only.

.. autofunction:: vlrdevapi.search.search_events
   :noindex:

search_series
~~~~~~~~~~~~~

Search for series only.

.. autofunction:: vlrdevapi.search.search_series
   :noindex:

Data Models
-----------

SearchResults
~~~~~~~~~~~~~

Container for all search results.

.. autoclass:: vlrdevapi.search.SearchResults
   :members:
   :undoc-members:

SearchPlayerResult
~~~~~~~~~~~~~~~~~~

Player search result with enriched data.

.. autoclass:: vlrdevapi.search.SearchPlayerResult
   :members:
   :undoc-members:

SearchTeamResult
~~~~~~~~~~~~~~~~

Team search result with enriched data.

.. autoclass:: vlrdevapi.search.SearchTeamResult
   :members:
   :undoc-members:

SearchEventResult
~~~~~~~~~~~~~~~~~

Event search result.

.. autoclass:: vlrdevapi.search.SearchEventResult
   :members:
   :undoc-members:

SearchSeriesResult
~~~~~~~~~~~~~~~~~~

Series search result.

.. autoclass:: vlrdevapi.search.SearchSeriesResult
   :members:
   :undoc-members:

Examples
--------

Basic Search
~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Search everything
   results = vlr.search.search("nrg")
   print(f"Found {results.total_results} results")

   # Access results by type
   for team in results.teams:
       status = "inactive" if team.is_inactive else "active"
       print(f"Team: {team.name} ({status}) - {team.country}")

   for player in results.players:
       print(f"Player: {player.ign} - {player.country}")

Type-Specific Searches
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Search only players
   players = vlr.search.search_players("tenz")
   for player in players:
       print(f"{player.ign} - {player.country}")

   # Search only teams
   teams = vlr.search.search_teams("sentinels")
   
   # Search only events
   events = vlr.search.search_events("champions")
