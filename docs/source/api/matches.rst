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
   matches = vlr.matches.upcoming(limit=5)
   for m in matches:
       print(f"{m.team1.name} vs {m.team2.name} - {m.event}")

Live Matches
~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   live = vlr.matches.live(limit=3)
   for m in live:
       print(f"LIVE: {m.team1.name} vs {m.team2.name}")

Completed Matches
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   results = vlr.matches.completed(limit=5)
   for m in results:
       print(f"{m.team1.name} {m.team1.score}-{m.team2.score} {m.team2.name}")

See more examples: :doc:`../examples`
