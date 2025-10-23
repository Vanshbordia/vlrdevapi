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

Get currently live matches. Supports an optional ``limit`` parameter to cap the number of returned matches (capped internally at 500 for consistency with other endpoints).

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

Team information in a match including name, ID, country, and score.

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

   # Get up to 5 currently live matches
   live = vlr.matches.live(limit=5)
   
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

* ``vlr.matches`` uses shared `httpx` clients with HTTP/2 and connection pooling, reducing latency for repeat calls.
* `Team.id` is filled opportunistically by scraping the match header; it may be ``None`` when the team is TBD or hidden on VLR.gg.
* Results are cached in process via ``vlr.fetcher``. Call ``vlr.fetcher.clear_cache()`` before refetching if you need fresh data.
* Return types use modern Python typing: ``list[Match]``, ``int | None``, and ``Literal['upcoming','live','completed']`` for ``Match.status``.

Pagination
~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   # Get a specific results page when no limit is supplied
   page1 = vlr.matches.completed(page=1)
   page2 = vlr.matches.completed(page=2)
