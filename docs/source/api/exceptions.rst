Exceptions
==========

The library defines custom exceptions for different error scenarios.

Exception Hierarchy
-------------------

.. code-block:: text

   VlrdevapiError (base exception)
   ├── NetworkError
   └── RateLimitError

Exception Classes
-----------------

VlrdevapiError
~~~~~~~~~~~

.. autoclass:: vlrdevapi.exceptions.VlrdevapiError
   :members:
   :undoc-members:

Base exception for all library errors.

NetworkError
~~~~~~~~~~~~

.. autoclass:: vlrdevapi.exceptions.NetworkError
   :members:
   :undoc-members:

Raised when network requests fail due to:

- Connection timeouts
- HTTP errors (4xx, 5xx)
- DNS resolution failures
- SSL/TLS errors

RateLimitError
~~~~~~~~~~~~~~

.. autoclass:: vlrdevapi.exceptions.RateLimitError
   :members:
   :undoc-members:

Raised when the server returns HTTP 429 (Too Many Requests).

Usage Examples
--------------

Basic Error Handling
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import NetworkError

   try:
       events = vlr.events.list_events()
   except NetworkError as e:
       print(f"Failed to fetch events: {e}")

Handle Rate Limiting
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import RateLimitError
   import time

   try:
       matches = vlr.matches.upcoming()
   except RateLimitError:
       print("Rate limited. Waiting before retry...")
       time.sleep(60)
       matches = vlr.matches.upcoming()

Catch All Library Errors
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import VlrdevapiError

   try:
       profile = vlr.players.profile(player_id=4164)
   except VlrdevapiError as e:
       print(f"API error: {e}")

Specific Error Handling
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import NetworkError, RateLimitError

   try:
       events = vlr.events.list_events()
   except RateLimitError:
       print("Rate limited. Please wait and try again.")
   except NetworkError as e:
       print(f"Network error: {e}")
       print("Check your internet connection.")

Retry Logic
~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import NetworkError, RateLimitError
   import time

   def fetch_with_retry(func, max_retries=3):
       for attempt in range(max_retries):
           try:
               return func()
           except RateLimitError:
               if attempt < max_retries - 1:
                   wait_time = 60 * (attempt + 1)
                   print(f"Rate limited. Waiting {wait_time}s...")
                   time.sleep(wait_time)
               else:
                   raise
           except NetworkError as e:
               if attempt < max_retries - 1:
                   print(f"Network error: {e}. Retrying...")
                   time.sleep(5)
               else:
                   raise

   # Use retry logic
   events = fetch_with_retry(lambda: vlr.events.list_events())

Logging Errors
~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import VlrdevapiError
   import logging

   logging.basicConfig(level=logging.ERROR)
   logger = logging.getLogger(__name__)

   try:
       matches = vlr.matches.upcoming()
   except VlrdevapiError as e:
       logger.error(f"Failed to fetch matches: {e}", exc_info=True)

Best Practices
--------------

Always Handle Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~

Network operations can fail. Always wrap API calls in try-except blocks:

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import NetworkError

   try:
       data = vlr.events.list_events()
   except NetworkError:
       # Handle error gracefully
       data = []

Be Specific
~~~~~~~~~~~

Catch specific exceptions when possible:

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi.exceptions import RateLimitError, NetworkError

   try:
       data = vlr.events.list_events()
   except RateLimitError:
       # Handle rate limiting specifically
       pass
   except NetworkError:
       # Handle other network errors
       pass

Respect Rate Limits
~~~~~~~~~~~~~~~~~~~

When rate limited, wait before retrying:

.. code-block:: python

   import vlrdevapi as vlr
   import time
   from vlrdevapi.exceptions import RateLimitError

   try:
       data = vlr.events.list_events()
   except RateLimitError:
       time.sleep(60)  # Wait at least 60 seconds
       data = vlr.events.list_events()

Use Library Caching
~~~~~~~~~~~~~~~~~~~

The library includes built-in caching to reduce requests:

.. code-block:: python

   import vlrdevapi as vlr

   # First call fetches from network
   events1 = vlr.events.list_events()
   
   # Second call uses cache (no network request)
   events2 = vlr.events.list_events()
   
   # Clear cache when you need fresh data
   vlr.fetcher.clear_cache()
   events3 = vlr.events.list_events()  # Fetches from network
