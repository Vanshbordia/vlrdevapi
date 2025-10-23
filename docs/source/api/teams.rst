Teams API
=========

The teams module provides access to team information, rosters, matches, tournament placements, and transaction history.

Overview
--------

Get comprehensive team data including team info, current rosters, match schedules, tournament placement history, and player transactions (joins, leaves, status changes).

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

transactions
~~~~~~~~~~~~

.. autofunction:: vlrdevapi.teams.transactions
   :noindex:

previous_players
~~~~~~~~~~~~~~~~

.. autofunction:: vlrdevapi.teams.previous_players
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

SuccessorTeam
~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.SuccessorTeam
   :members:
   :undoc-members:

RosterMember
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.RosterMember
   :members:
   :undoc-members:

MatchTeam
~~~~~~~~~

.. autoclass:: vlrdevapi.teams.MatchTeam
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

PlayerTransaction
~~~~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.PlayerTransaction
   :members:
   :undoc-members:

PreviousPlayer
~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.teams.PreviousPlayer
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
   if team_info:
       print(f"{team_info.name} ({team_info.tag})")
       print(f"Country: {team_info.country}")
       print(f"Active: {team_info.is_active}")
   else:
       print("Team not found")
   
   # Access social links
   if team_info and team_info.socials:
       for social in team_info.socials:
           print(f"{social.label}: {social.url}")

Get Team Roster
~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get current roster
   roster = vlr.teams.roster(team_id=799)
   
   for member in roster:
       print(f"{member.ign} - {member.real_name or 'N/A'}")
       print(f"  Role: {member.role}")
       if member.country:
           print(f"  Country: {member.country}")

Get Team Matches
~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get upcoming matches (with pagination)
   upcoming = vlr.teams.upcoming_matches(team_id=799, limit=10)
   
   for match in upcoming:
       print(f"{match.team1.name} vs {match.team2.name}")
       print(f"Tournament: {match.tournament_name}")
       if match.match_datetime:
           print(f"Date: {match.match_datetime.strftime('%B %d, %Y at %I:%M %p')}")
   
   # Get completed matches (with pagination)
   completed = vlr.teams.completed_matches(team_id=799, limit=20)
   
   for match in completed:
       print(f"{match.team1.name} {match.team1.score} - {match.team2.score} {match.team2.name}")
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

Get Team Transactions
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get all transactions for a team
   txns = vlr.teams.transactions(team_id=1034)
   
   for txn in txns[:5]:
       if txn.date:
           print(f"{txn.date.strftime('%Y/%m/%d')}: {txn.ign} - {txn.action} ({txn.position})")
       else:
           print(f"Unknown: {txn.ign} - {txn.action} ({txn.position})")

Get Previous Players
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get all previous/current players with calculated status
   players = vlr.teams.previous_players(team_id=1034)
   
   # Filter by status
   active = [p for p in players if p.status == "Active"]
   left = [p for p in players if p.status == "Left"]
   
   print(f"Active: {len(active)}, Left: {len(left)}")
   
   # Display player details
   for player in active:
       print(f"{player.ign} - {player.position}")
       if player.join_date:
           print(f"  Joined: {player.join_date.strftime('%Y/%m/%d')}")
       else:
           print(f"  Joined: Unknown")
   
   # Players can rejoin after leaving - status is based on most recent action
   for player in players:
       if len([t for t in player.transactions if t.action == "join"]) > 1:
           print(f"{player.ign} has rejoined the team")

Pagination
~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get specific number of matches
   matches_2 = vlr.teams.completed_matches(team_id=799, limit=2)
   matches_5 = vlr.teams.completed_matches(team_id=799, limit=5)
   
   print(f"Retrieved {len(matches_2)} matches")
   print(f"Retrieved {len(matches_5)} matches")
   

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
   recent = vlr.teams.completed_matches(team_id=team_id, limit=5)
   print(f"\nLast 5 matches:")
   for match in recent:
       result = f"{match.team1.score}-{match.team2.score}"
       print(f"  {match.team1.name} vs {match.team2.name}: {result}")
       if match.match_datetime:
           print(f"    Date: {match.match_datetime.strftime('%B %d, %Y')}")
   
   # Get placements
   placements = vlr.teams.placements(team_id=team_id)
   print(f"\nTotal events participated: {len(placements)}")
   
   # Show top 3 recent placements
   for placement in placements[:3]:
       print(f"\n{placement.event_name} ({placement.year})")
       for detail in placement.placements:
           print(f"  {detail.series}: {detail.place} - {detail.prize_money}")
