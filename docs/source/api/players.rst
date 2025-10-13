Players API
===========

The players module provides access to player profiles, match history, and statistics.

Module Overview
---------------

.. automodule:: vlrdevapi.players
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

profile
~~~~~~~

.. autofunction:: vlrdevapi.players.profile
   :noindex:

matches
~~~~~~~

.. autofunction:: vlrdevapi.players.matches
   :noindex:

agent_stats
~~~~~~~~~~~

.. autofunction:: vlrdevapi.players.agent_stats
   :noindex:

Data Models
-----------

SocialLink
~~~~~~~~~~

.. autoclass:: vlrdevapi.players.SocialLink
   :members:
   :undoc-members:

Team
~~~~

.. autoclass:: vlrdevapi.players.Team
   :members:
   :undoc-members:

Profile
~~~~~~~

.. autoclass:: vlrdevapi.players.Profile
   :members:
   :undoc-members:

MatchTeam
~~~~~~~~~

.. autoclass:: vlrdevapi.players.MatchTeam
   :members:
   :undoc-members:

Match
~~~~~

.. autoclass:: vlrdevapi.players.Match
   :members:
   :undoc-members:

AgentStats
~~~~~~~~~~

.. autoclass:: vlrdevapi.players.AgentStats
   :members:
   :undoc-members:

Usage Examples
--------------

Get Player Profile
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get player profile
   profile = vlr.players.profile(player_id=4164)
   
   print(f"Handle: {profile.handle}")
   print(f"Real Name: {profile.real_name}")
   print(f"Country: {profile.country}")
   
   # Current teams
   for team in profile.current_teams:
       print(f"Team: {team.name} ({team.role})")
   
   # Social links
   for social in profile.socials:
       print(f"{social.label}: {social.url}")

Get Player Match History
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get recent matches
   matches = vlr.players.matches(player_id=4164, limit=20)
   
   for match in matches:
       print(f"{match.player_team.name} vs {match.opponent_team.name}")
       print(f"Result: {match.result}")
       print(f"Score: {match.player_score}-{match.opponent_score}")
       print(f"Event: {match.event}")
       print()

Get Agent Statistics
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get agent stats for past 60 days
   stats = vlr.players.agent_stats(player_id=4164, timespan="60d")
   
   for stat in stats:
       if stat.agent and stat.agent != "All":
           print(f"{stat.agent}:")
           print(f"  Games: {stat.usage_count}")
           print(f"  Rating: {stat.rating}")
           print(f"  ACS: {stat.acs}")
           print(f"  K/D: {stat.kd}")
           print(f"  KAST: {stat.kast * 100:.1f}%")
           print()

Different Time Periods
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Available timespans: "30d", "60d", "90d", "all"
   
   # Last 30 days
   stats_30d = vlr.players.agent_stats(player_id=4164, timespan="30d")
   
   # All time
   stats_all = vlr.players.agent_stats(player_id=4164, timespan="all")
