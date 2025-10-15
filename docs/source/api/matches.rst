Matches API
===========

The matches module provides access to match schedules and results including upcoming, live, and completed matches.

Overview
--------

Track Valorant esports matches across all tournaments and events. Get real-time updates on live matches, upcoming schedules, and historical results.

.. automodule:: vlrdevapi.matches
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

upcoming
~~~~~~~~

Get upcoming scheduled matches.

.. autofunction:: vlrdevapi.matches.upcoming
   :noindex:

live
~~~~

Get currently live matches.

.. autofunction:: vlrdevapi.matches.live
   :noindex:

completed
~~~~~~~~~

Get recently completed matches.

.. autofunction:: vlrdevapi.matches.completed
   :noindex:

Data Models
-----------

Team
~~~~

Team information in a match including name, short tag, ID, country, and score.

.. autoclass:: vlrdevapi.matches.Team
   :members:
   :undoc-members:

Match
~~~~~

Match information including teams, scores, and event details.

.. autoclass:: vlrdevapi.matches.Match
   :members:
   :undoc-members:

Examples
--------

Upcoming Matches
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get next 10 upcoming matches (excludes live matches)
   matches = vlr.matches.upcoming(limit=10)
   
   for match in matches:
       print(f"{match.team1.name} vs {match.team2.name}")
       print(f"Countries: {match.team1.country} vs {match.team2.country}")
       print(f"Event: {match.event}")
       print(f"Time: {match.time}")
       print(f"Status: {match.status}")  # Will always be 'upcoming'

Live Matches
~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get currently live matches only
   live = vlr.matches.live()
   
   for match in live:
       print(f"LIVE: {match.team1.name} vs {match.team2.name}")
       print(f"Event: {match.event}")
       if match.team1.score is not None:
           print(f"Current Score: {match.team1.score}-{match.team2.score}")

Completed Matches
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get recent completed results only
   results = vlr.matches.completed(limit=10)
   
   for match in results:
       print(f"{match.team1.name} vs {match.team2.name}")
       score = f"{match.team1.score}-{match.team2.score}"
       print(f"Final Score: {score}")
       print(f"Status: {match.status}")  # Will always be 'completed'

Performance Notes
-----------------

* By default, ``Team.id`` and ``Team.tag`` fields will be ``None`` for performance reasons.
* To populate these fields, pass ``enrich_teams=True`` to any match function. This will fetch team metadata from the series page header for each match, which is significantly slower but provides complete team information.
* The enrichment does not rely on URL patterns and fetches authoritative data from the match page header.

.. code-block:: python

   # Fast (default) - id and tag will be None
   matches = vlr.matches.upcoming(limit=10)
   
   # Slower but complete - id and tag will be populated
   matches = vlr.matches.upcoming(limit=10, enrich_teams=True)
   for match in matches:
       print(f"{match.team1.name} ({match.team1.tag}) [ID: {match.team1.id}]")

Pagination
~~~~~~~~~~

.. code-block:: python

   # Get specific page
   page1 = vlr.matches.completed(limit=10, page=1)
   page2 = vlr.matches.completed(limit=10, page=2)
