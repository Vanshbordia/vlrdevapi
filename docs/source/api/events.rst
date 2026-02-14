Events API
==========

The events module provides access to Valorant esports events, tournaments, and competitions.

Overview
--------

Access VCT Champions, VCT Masters, regional leagues, Game Changers tournaments, and other Valorant esports events. Get event details, matches, and standings.

.. automodule:: vlrdevapi.events
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

info
~~~~

.. autofunction:: vlrdevapi.events.info
   :noindex:

list_events
~~~~~~~~~~~

.. autofunction:: vlrdevapi.events.list_events
   :noindex:

match_summary
~~~~~~~~~~~~~

.. autofunction:: vlrdevapi.events.match_summary
   :noindex:

matches
~~~~~~~

.. autofunction:: vlrdevapi.events.matches
   :noindex:

stages
~~~~~~

.. autofunction:: vlrdevapi.events.stages
   :noindex:

standings
~~~~~~~~~

.. autofunction:: vlrdevapi.events.standings
   :noindex:

teams
~~~~~

.. autofunction:: vlrdevapi.events.teams
   :noindex:

Enums
-----

EventTier
~~~~~~~~~

.. autoclass:: vlrdevapi.events.EventTier
   :members:
   :undoc-members:

EventStatus
~~~~~~~~~~~

.. autoclass:: vlrdevapi.events.EventStatus
   :members:
   :undoc-members:

Data Models
-----------

EventStage
~~~~~~~~~~

.. autoclass:: vlrdevapi.events.EventStage
   :members:
   :undoc-members:

Info
~~~~

.. autoclass:: vlrdevapi.events.Info
   :members:
   :undoc-members:

ListEvent
~~~~~~~~~

.. autoclass:: vlrdevapi.events.ListEvent
   :members:
   :undoc-members:

Match
~~~~~

.. autoclass:: vlrdevapi.events.Match
   :members:
   :undoc-members:

MatchSummary
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.events.MatchSummary
   :members:
   :undoc-members:

MatchTeam
~~~~~~~~~

.. autoclass:: vlrdevapi.events.MatchTeam
   :members:
   :undoc-members:

StageMatches
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.events.StageMatches
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

Team
~~~~

.. autoclass:: vlrdevapi.events.Team
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
   info = vlr.events.info(event_id=2283)
   print(f"{info.name}")
   print(f"Prize: {info.prize}")
   print(f"Location: {info.location}")
   
   # Access parsed dates
   if info.start_date:
       print(f"Start Date: {info.start_date}")
   if info.end_date:
       print(f"End Date: {info.end_date}")

Get Event Matches
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get all matches for an event
   matches = vlr.events.matches(event_id=2498)

   for match in matches:
       print(f"{match.teams[0].name} vs {match.teams[1].name}")
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

Get Event Teams
~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get teams participating in an event
   teams = vlr.events.teams(event_id=2682)

   for team in teams:
       print(f"{team.name} (ID: {team.id})")
       if team.type:
           print(f"  Type: {team.type}")

See more examples: :doc:`../examples`
