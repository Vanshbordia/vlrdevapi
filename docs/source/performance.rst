Performance
===========

vlrdevapi is optimized for speed with several performance enhancements.

Optimizations
-------------

HTTP Connection Pooling
~~~~~~~~~~~~~~~~~~~~~~~

The library maintains persistent HTTP connections with keep-alive.

**Impact**: 2-3x faster network requests

In-Memory Caching
~~~~~~~~~~~~~~~~~

Responses are cached in memory to avoid redundant network requests.

**Impact**: 200-500x faster for repeated requests

Fast HTML Parser
~~~~~~~~~~~~~~~~

Uses lxml, a C-based parser instead of Python's html.parser.

**Impact**: 50-100% faster HTML parsing

Gzip Compression
~~~~~~~~~~~~~~~~

Automatically accepts and decompresses gzip-encoded responses.

**Impact**: 5-10x smaller transfers

Cache Management
----------------

.. code-block:: python

   import vlrdevapi as vlr

   # Clear cache for fresh data
   vlr.fetcher.clear_cache()

   # Close connections on shutdown
   vlr.fetcher.close_connections()
