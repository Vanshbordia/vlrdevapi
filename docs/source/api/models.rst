Data Models
===========

All data returned by vlrdevapi is structured using Pydantic models with full type hints and validation.

Model Features
--------------

All models are:

- **Immutable**: Models are frozen and cannot be modified after creation
- **Type-safe**: Full type hints for all fields
- **Validated**: Pydantic validates data on creation
- **Serializable**: Can be converted to dict or JSON

Common Patterns
---------------

Accessing Model Data
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Get a model instance
   profile = vlr.players.profile(player_id=4164)
   
   # Access fields directly
   print(profile.handle)
   print(profile.real_name)
   print(profile.country)
   
   # Models are immutable
   # profile.handle = "new_name"  # This will raise an error

Converting to Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   profile = vlr.players.profile(player_id=4164)
   
   # Convert to dict
   data = profile.model_dump()
   print(data)
   
   # Convert to JSON
   json_str = profile.model_dump_json()

Optional Fields
~~~~~~~~~~~~~~~

Many fields are optional and may be None:

.. code-block:: python

   import vlrdevapi as vlr

   match = vlr.matches.upcoming()[0]
   
   # Check if optional field exists
   if match.match_datetime:
       print(f"Date: {match.match_datetime.strftime('%Y-%m-%d %H:%M')}")
   else:
       print("Date not available")

Lists and Tuples
~~~~~~~~~~~~~~~~

Some fields contain lists or tuples:

.. code-block:: python

   import vlrdevapi as vlr

   # Tuple of exactly 2 teams
   match = vlr.matches.upcoming()[0]
   team1, team2 = match.teams
   
   # List of variable length
   profile = vlr.players.profile(player_id=4164)
   for team in profile.current_teams:
       print(team.name)

Events Models
-------------

See :doc:`events` for detailed documentation of:

- ListEvent
- Info
- MatchTeam
- Match
- StageMatches
- MatchSummary
- StandingEntry
- Standings

Matches Models
--------------

See :doc:`matches` for detailed documentation of:

- Match

Players Models
--------------

See :doc:`players` for detailed documentation of:

- SocialLink
- Team
- Profile
- MatchTeam
- Match
- AgentStats

Series Models
-------------

See :doc:`series` for detailed documentation of:

- TeamInfo
- MapAction
- Info
- PlayerStats
- MapTeamScore
- RoundResult
- MapPlayers

Field Types
-----------

Common field types used across models:

Primitive Types
~~~~~~~~~~~~~~~

- **int**: Integer values (IDs, scores, counts)
- **float**: Decimal values (ratings, percentages)
- **str**: Text values (names, URLs)
- **bool**: Boolean flags (is_winner, etc.)

Date and Time
~~~~~~~~~~~~~

- **datetime.date**: Date values (match dates, join dates)
- **datetime.time**: Time values (match times)

Collections
~~~~~~~~~~~

- **List[T]**: Variable-length lists
- **Tuple[T, T]**: Fixed-length tuples (usually 2 teams)
- **Optional[T]**: Values that may be None

Literals
~~~~~~~~

- **Literal["a", "b"]**: String values restricted to specific options

Example: status field can only be "upcoming", "live", or "completed"

Validation
----------

Pydantic validates all data:

.. code-block:: python

   from vlrdevapi.events import ListEvent
   
   # Valid data
   event = ListEvent(
       id=123,
       name="Champions 2025",
       status="ongoing",
       url="https://www.vlr.gg/event/123"
   )
   
   # Invalid status will raise ValidationError
   # event = ListEvent(
   #     id=123,
   #     name="Champions 2025",
   #     status="invalid",  # Not in allowed values
   #     url="https://www.vlr.gg/event/123"
   # )

Best Practices
--------------

Type Hints
~~~~~~~~~~

Use type hints when working with models:

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.players import Profile
   
   def print_player_info(profile: Profile) -> None:
       print(f"{profile.handle} from {profile.country}")
   
   profile = vlr.players.profile(player_id=4164)
   print_player_info(profile)

None Checks
~~~~~~~~~~~

Always check optional fields before use:

.. code-block:: python

   import vlrdevapi as vlr

   match = vlr.matches.upcoming()[0]
   
   # Safe access
   if match.match_datetime:
       print(f"Date: {match.match_datetime.isoformat()}")
   
   # Or use default value
   date_str = match.match_datetime.isoformat() if match.match_datetime else "TBD"

Iteration
~~~~~~~~~

Iterate over lists safely:

.. code-block:: python

   import vlrdevapi as vlr

   profile = vlr.players.profile(player_id=4164)
   
   # Check if list has items
   if profile.current_teams:
       for team in profile.current_teams:
           print(team.name)
   else:
       print("No current teams")
