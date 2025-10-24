Configuration
=============

The `vlrdevapi` library provides a global configuration system that allows you to customize
timeouts, retries, backoff, base URL, default User-Agent, and rate limiting behavior
at runtime.

This page describes how to configure the client and what options are available.

.. contents:: On this page
   :local:
   :depth: 2

Overview
--------

Configuration is exposed via two top-level helpers:

- ``vlr.configure(...)``: Update one or more global settings.
- ``vlr.reset_config()``: Reset all settings back to library defaults.

These settings are consumed across the package by modules such as ``fetcher``, ``events``,
``series``, ``matches``, ``players``, ``teams``, and ``search``. The defaults are applied
lazily at call time, so changes take effect immediately without re-importing modules.

Available Options
-----------------

You can set any of the following options via ``vlr.configure``:

- ``vlr_base``
  The base URL for VLR.gg. Defaults to ``"https://www.vlr.gg"``.

- ``default_timeout``
  Default timeout in seconds for HTTP requests. Defaults to ``5.0``.

- ``default_user_agent``
  Default User-Agent header used for requests. Defaults to a Chrome-like UA string.

- ``max_retries``
  Maximum number of retries for failed requests in the fetcher. Defaults to ``3``.

- ``backoff_factor``
  Exponential backoff multiplier used by the fetcher. Defaults to ``1.0``.

- ``default_rate_limit``
  The default requests-per-second limit for built-in rate limiting. Defaults to ``10``.

- ``default_rate_limit_enabled``
  Whether rate limiting is enabled by default. Defaults to ``True``.

Quick Examples
--------------

Increase HTTP timeout and retries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Increase default timeout and retry behavior
   vlr.configure(default_timeout=10.0, max_retries=5, backoff_factor=2.0)

   # Calls now use the new defaults without code changes
   events = vlr.events.list_events(limit=5)

Customize User-Agent
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Set a custom User-Agent string for all outbound requests
   vlr.configure(default_user_agent="MyApp/1.0 (+https://example.com)")

Change Base URL (advanced)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import vlrdevapi as vlr

   # Point to an alternate origin or proxy if needed
   vlr.configure(vlr_base="https://my-proxy.example.com")

Rate Limiting
-------------

The library supports basic requests-per-second limiting using a lightweight token
bucket. You can control whether it is enabled and what the default rate is via the
configuration system.

To update global rate limiting behavior at runtime:

.. code-block:: python

   import vlrdevapi as vlr

   # Disable rate limiting
   vlr.configure(default_rate_limit_enabled=False)

   # Enable and set to 20 requests per second
   vlr.configure(default_rate_limit=20, default_rate_limit_enabled=True)

You can also adjust rate limiting during execution using the dedicated helpers in
``vlr.fetcher``:

.. code-block:: python

   import vlrdevapi as vlr

   # Reduce rate temporarily for a critical section
   vlr.configure_rate_limit(requests_per_second=5, enabled=True)

   # Reset to your configured defaults (reads from vlr.configure values)
   vlr.reset_rate_limit()

Reset to Defaults
-----------------

To restore all configuration values back to the package defaults:

.. code-block:: python

   import vlrdevapi as vlr

   vlr.reset_config()

Interaction With fetcher
------------------------

The ``fetcher`` module uses these configuration values when computing request headers,
timeouts, retry counts, and backoff. You can override any of these per-call by passing
parameters to the public functions:

.. code-block:: python

   from vlrdevapi.fetcher import fetch_html

   # Override timeout and user agent just for this call
   html = fetch_html(
       url="https://www.vlr.gg/matches",
       timeout=2.5,
   )

Notes
-----

- Configuration takes effect immediately. There is no need to re-import modules.
- If you set an option to ``None``, the previous value is retained.
