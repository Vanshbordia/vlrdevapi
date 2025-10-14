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

   # Get next 10 matches
   matches = vlr.matches.upcoming(limit=10)
   
   for match in matches:
       print(f"{match.teams[0]} vs {match.teams[1]}")
       print(f"Event: {match.event}")
       print(f"Time: {match.time}")

Live Matches
~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get live matches
   live = vlr.matches.live()
   
   for match in live:
       print(f"LIVE: {match.teams[0]} vs {match.teams[1]}")
       print(f"Event: {match.event}")

Completed Matches
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get recent results
   results = vlr.matches.completed(limit=10)
   
   for match in results:
       print(f"{match.teams[0]} vs {match.teams[1]}")
       print(f"Score: {match.score}")

Pagination
~~~~~~~~~~

.. code-block:: python

   # Get specific page
   page1 = vlr.matches.completed(limit=10, page=1)
   page2 = vlr.matches.completed(limit=10, page=2)
