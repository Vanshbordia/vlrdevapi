Teams API
=========

The teams module provides access to Valorant esports team information, rosters, match history, and event placements.

Module Overview
---------------

.. automodule:: vlrdevapi.teams
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

info
~~~~

.. autofunction:: vlrdevapi.teams.info
   :noindex:

roster
~~~~~~

.. autofunction:: vlrdevapi.teams.roster
   :noindex:

upcoming_matches
~~~~~~~~~~~~~~~~

.. autofunction:: vlrdevapi.teams.upcoming_matches
   :noindex:

completed_matches
~~~~~~~~~~~~~~~~~

.. autofunction:: vlrdevapi.teams.completed_matches
   :noindex:

placements
~~~~~~~~~~

.. autofunction:: vlrdevapi.teams.placements
   :noindex:

Data Models
-----------

TeamInfo
~~~~~~~~

.. autoclass:: vlrdevapi.teams.TeamInfo
   :members:
   :undoc-members:

SocialLink
~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.SocialLink
   :members:
   :undoc-members:

PreviousTeam
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.PreviousTeam
   :members:
   :undoc-members:

RosterMember
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.RosterMember
   :members:
   :undoc-members:

TeamMatch
~~~~~~~~~

.. autoclass:: vlrdevapi.teams.TeamMatch
   :members:
   :undoc-members:

EventPlacement
~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.EventPlacement
   :members:
   :undoc-members:

PlacementDetail
~~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.PlacementDetail
   :members:
   :undoc-members:

Usage Examples
--------------

Get Team Information
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get team information
   team_info = vlr.teams.info(team_id=799)
   print(f"{team_info.name} ({team_info.tag})")
   print(f"Country: {team_info.country}")
   print(f"Active: {team_info.is_active}")
   
   # Access social links
   for social in team_info.socials:
       print(f"{social.platform}: {social.url}")

Get Team Roster
~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get current roster
   roster = vlr.teams.roster(team_id=799)
   
   for member in roster:
       print(f"{member.ign} - {member.name}")
       print(f"  Role: {member.role}")
       if member.country:
           print(f"  Country: {member.country}")

Get Team Matches
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get upcoming matches (with pagination)
   upcoming = vlr.teams.upcoming_matches(team_id=799, count=10)
   
   for match in upcoming:
       print(f"{match.team1_name} vs {match.team2_name}")
       print(f"Tournament: {match.tournament_name}")
       print(f"Date: {match.date} {match.time}")
   
   # Get completed matches (with pagination)
   completed = vlr.teams.completed_matches(team_id=799, count=20)
   
   for match in completed:
       print(f"{match.team1_name} {match.score_team1} - {match.score_team2} {match.team2_name}")
       print(f"Tournament: {match.tournament_name}")

Get Event Placements
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get all event placements for a team
   placements = vlr.teams.placements(team_id=799)
   
   for placement in placements:
       print(f"\n{placement.event_name} ({placement.year})")
       print(f"Event ID: {placement.event_id}")
       
       # Each event can have multiple placements (e.g., groups, playoffs)
       for detail in placement.placements:
           print(f"  {detail.series} - {detail.place}")
           if detail.prize_money:
               print(f"    Prize: {detail.prize_money}")

Pagination
~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get specific number of matches
   matches_10 = vlr.teams.completed_matches(team_id=799, count=10)
   matches_50 = vlr.teams.completed_matches(team_id=799, count=50)
   
   # Get all matches (no limit)
   all_matches = vlr.teams.completed_matches(team_id=799)
   
   print(f"Retrieved {len(matches_10)} matches")
   print(f"Retrieved {len(matches_50)} matches")
   print(f"Total matches: {len(all_matches)}")

Complete Example
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Comprehensive team analysis
   team_id = 799  # Velocity Gaming
   
   # Get team info
   info = vlr.teams.info(team_id=team_id)
   print(f"Team: {info.name} ({info.tag})")
   print(f"Region: {info.country}")
   
   # Get roster
   roster = vlr.teams.roster(team_id=team_id)
   print(f"\nRoster: {len(roster)} players")
   
   # Get recent matches
   recent = vlr.teams.completed_matches(team_id=team_id, count=5)
   print(f"\nLast 5 matches:")
   for match in recent:
       result = f"{match.score_team1}-{match.score_team2}"
       print(f"  {match.team1_name} vs {match.team2_name}: {result}")
   
   # Get placements
   placements = vlr.teams.placements(team_id=team_id)
   print(f"\nTotal events participated: {len(placements)}")
   
   # Show top 3 recent placements
   for placement in placements[:3]:
       print(f"\n{placement.event_name} ({placement.year})")
       for detail in placement.placements:
           print(f"  {detail.series}: {detail.place} - {detail.prize_money}")
