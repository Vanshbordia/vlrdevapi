Constants
=========

Core configuration constants used throughout ``vlrdevapi``.

These values are defined in ``vlrdevapi.constants`` and are read-only. Behavior such as
timeouts, retries, and rate limiting are applied by higher-level helpers.

List of constants
-----------------

- ``VLR_BASE``: Base URL for VLR.gg.
- ``DEFAULT_TIMEOUT``: Default HTTP timeout in seconds.
- ``DEFAULT_USER_AGENT``: Default User-Agent header for network requests.
- ``MAX_RETRIES``: Maximum retry attempts for transient HTTP errors.
- ``BACKOFF_FACTOR``: Exponential backoff multiplier between retries.
- ``DEFAULT_RATE_LIMIT``: Default requests-per-second (RPS) limit.
- ``DEFAULT_RATE_LIMIT_ENABLED``: Whether rate limiting is enabled by default.

Examples
--------

.. code-block:: python

   import vlrdevapi as vlr
   from vlrdevapi import constants

   print(constants.VLR_BASE)
   print(constants.DEFAULT_TIMEOUT)

.. code-block:: python

   import vlrdevapi as vlr
   # Change rate limiting using helpers (do not modify constants directly)
   vlr.configure_rate_limit(requests_per_second=5.0, enabled=True)
   vlr.reset_rate_limit()  # restore defaults

See also
--------

- :doc:`rate-limiting`
