Players API
===========

The players module provides access to player profiles, match history, and agent statistics.

Overview
--------

Get comprehensive player data including profiles, team history, match records, and agent performance statistics.

.. automodule:: vlrdevapi.players
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

profile
~~~~~~~

Get player profile information.

.. autofunction:: vlrdevapi.players.profile
   :noindex:

matches
~~~~~~~

Get player match history.

.. autofunction:: vlrdevapi.players.matches
   :noindex:

agent_stats
~~~~~~~~~~~

Get player agent statistics.

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

Examples
--------

Player Profile
~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get player profile
   profile = vlr.players.profile(player_id=4164)
   
   print(f"{profile.handle} ({profile.real_name})")
   print(f"Country: {profile.country}")
   
   # Current teams
   for team in profile.current_teams:
       print(f"Team: {team.name} - {team.role}")

Match History
~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get recent matches
   matches = vlr.players.matches(player_id=4164, limit=20)
   
   for match in matches:
       print(f"{match.player_team.name} vs {match.opponent_team.name}")
       print(f"Event: {match.event}")
       # Stage and phase information
       if match.stage:
           stage_info = f"{match.stage}"
           if match.phase:
               stage_info += f" - {match.phase}"
           print(f"Stage: {stage_info}")
       print(f"Result: {match.result}")
       if match.player_score is not None:
           print(f"Score: {match.player_score}-{match.opponent_score}")

Agent Statistics
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get agent stats
   stats = vlr.players.agent_stats(player_id=4164, timespan="60d")
   
   for stat in stats[:5]:
       if stat.agent and stat.agent != "All":
           print(f"{stat.agent}: {stat.rating:.2f} rating, {stat.acs:.0f} ACS")

Timespan Options
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Available timespans: "30d", "60d", "90d", "all"
   stats_30d = vlr.players.agent_stats(player_id=4164, timespan="30d")
   stats_all = vlr.players.agent_stats(player_id=4164, timespan="all")
