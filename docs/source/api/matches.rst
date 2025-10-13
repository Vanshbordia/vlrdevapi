Matches API
===========

The matches module provides access to match schedules and results.

Module Overview
---------------

.. automodule:: vlrdevapi.matches
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

upcoming
~~~~~~~~

.. autofunction:: vlrdevapi.matches.upcoming
   :noindex:

live
~~~~

.. autofunction:: vlrdevapi.matches.live
   :noindex:

completed
~~~~~~~~~

.. autofunction:: vlrdevapi.matches.completed
   :noindex:

Data Models
-----------

Match
~~~~~

.. autoclass:: vlrdevapi.matches.Match
   :members:
   :undoc-members:

Usage Examples
--------------

Get Upcoming Matches
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get next 10 upcoming matches
   matches = vlr.matches.upcoming(limit=10)
   
   for match in matches:
       print(f"{match.teams[0]} vs {match.teams[1]}")
       print(f"Event: {match.event}")
       print(f"Time: {match.time}")
       print()

Get Live Matches
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get currently live matches
   live_matches = vlr.matches.live()
   
   if not live_matches:
       print("No live matches")
   else:
       for match in live_matches:
           print(f"LIVE: {match.teams[0]} vs {match.teams[1]}")
           print(f"Event: {match.event}")

Get Completed Matches
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get recent completed matches
   results = vlr.matches.completed(limit=10)
   
   for match in results:
       print(f"{match.teams[0]} vs {match.teams[1]}")
       print(f"Score: {match.score}")
       print(f"Event: {match.event}")
       print()

Pagination
~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get second page of results
   page2 = vlr.matches.completed(limit=10, page=2)
