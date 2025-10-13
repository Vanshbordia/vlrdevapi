Events API
==========

The events module provides access to Valorant esports events, tournaments, and competitions including VCT Champions, VCT Masters, regional leagues, and Game Changers tournaments.

Module Overview
---------------

.. automodule:: vlrdevapi.events
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

list_events
~~~~~~~~~~~

.. autofunction:: vlrdevapi.events.list_events
   :noindex:

info
~~~~

.. autofunction:: vlrdevapi.events.info
   :noindex:

matches
~~~~~~~

.. autofunction:: vlrdevapi.events.matches
   :noindex:

match_summary
~~~~~~~~~~~~~

.. autofunction:: vlrdevapi.events.match_summary
   :noindex:

standings
~~~~~~~~~

.. autofunction:: vlrdevapi.events.standings
   :noindex:

Data Models
-----------

ListEvent
~~~~~~~~~

.. autoclass:: vlrdevapi.events.ListEvent
   :members:
   :undoc-members:

Info
~~~~

.. autoclass:: vlrdevapi.events.Info
   :members:
   :undoc-members:

MatchTeam
~~~~~~~~~

.. autoclass:: vlrdevapi.events.MatchTeam
   :members:
   :undoc-members:

Match
~~~~~

.. autoclass:: vlrdevapi.events.Match
   :members:
   :undoc-members:

StageMatches
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.events.StageMatches
   :members:
   :undoc-members:

MatchSummary
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.events.MatchSummary
   :members:
   :undoc-members:

StandingEntry
~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.events.StandingEntry
   :members:
   :undoc-members:

Standings
~~~~~~~~~

.. autoclass:: vlrdevapi.events.Standings
   :members:
   :undoc-members:

Usage Examples
--------------

List Events
~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # List all VCT events
   events = vlr.events.list_events(tier="vct")
   
   # Filter by status
   ongoing = vlr.events.list_events(tier="vct", status="ongoing")
   
   # Filter by region
   na_events = vlr.events.list_events(tier="vct", region="na")

Get Event Details
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get event information
   info = vlr.events.info(event_id=2498)
   print(f"{info.name}")
   print(f"Prize: {info.prize}")
   print(f"Location: {info.location}")

Get Event Matches
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get all matches for an event
   matches = vlr.events.matches(event_id=2498)
   
   for match in matches:
       team1, team2 = match.teams
       print(f"{team1.name} vs {team2.name}")
       print(f"Status: {match.status}")

Get Event Standings
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get event standings/prize distribution
   standings = vlr.events.standings(event_id=2498)
   
   for entry in standings.entries:
       print(f"{entry.place}. {entry.team_name}")
       if entry.prize:
           print(f"   Prize: {entry.prize}")
