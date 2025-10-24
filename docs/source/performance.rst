Performance
===========

vlrdevapi is optimized for speed and efficiency.

Built-in Optimizations
----------------------

HTTP Connection Pooling & HTTP/2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Managed by the shared `httpx` clients with automatic keep-alive and HTTP/2 support.

- **Impact**: Lower latency from multiplexed requests and persistent sessions
- Shared across the process for consistent performance

In-Memory Caching
~~~~~~~~~~~~~~~~~

Responses cached in memory to avoid redundant requests.

- **Impact**: Orders-of-magnitude faster for repeated requests within a session
- Cache is in-memory only; call ``vlr.fetcher.clear_cache()`` for fresh data

Fast HTML Parser
~~~~~~~~~~~~~~~~

Uses lxml (C-based) instead of Python's html.parser.

- **Impact**: 50-100% faster HTML parsing
- Installed automatically as a dependency

Brotli & Gzip Compression
~~~~~~~~~~~~~~~~~~~~~~~~~

`httpx` transparently negotiates Brotli (`br`) and gzip compression with VLR.gg.

- **Impact**: Smaller payloads and faster decompression
- Enabled by default; no additional configuration needed

Best Practices
--------------

Cache Management
~~~~~~~~~~~~~~~~

Clear cache when you need fresh data:

.. code-block:: python

   import vlrdevapi as vlr

   # Clear cache for fresh data
   vlr.fetcher.clear_cache()
   
   # Now fetch fresh data
   results = vlr.search.search("nrg")

Connection Cleanup
~~~~~~~~~~~~~~~~~~

Close connections on application shutdown:

.. code-block:: python

   import vlrdevapi as vlr
   # At application exit
   vlr.fetcher.close_connections()

Controlled Fetches
~~~~~~~~~~~~~~~~~~

Minimize API calls by batching or paginating operations:

.. code-block:: python

   import vlrdevapi as vlr
   # Efficient: Request a larger batch once
   matches = vlr.matches.upcoming(limit=5)

.. code-block:: python

   import vlrdevapi as vlr
   # Paginate when you need historical data
   page1 = vlr.matches.completed(limit=5, page=1)
   page2 = vlr.matches.completed(limit=5, page=2)
