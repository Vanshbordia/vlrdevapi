Performance
===========

vlrdevapi is optimized for speed and efficiency.

Built-in Optimizations
----------------------

HTTP Connection Pooling
~~~~~~~~~~~~~~~~~~~~~~~

Persistent HTTP connections with keep-alive.

- **Impact**: 2-3x faster network requests
- Automatically managed by the library

In-Memory Caching
~~~~~~~~~~~~~~~~~

Responses cached in memory to avoid redundant requests.

- **Impact**: 200-500x faster for repeated requests
- Automatic cache invalidation

Fast HTML Parser
~~~~~~~~~~~~~~~~

Uses lxml (C-based) instead of Python's html.parser.

- **Impact**: 50-100% faster HTML parsing
- Installed automatically as a dependency

Gzip Compression
~~~~~~~~~~~~~~~~

Automatic gzip compression for network transfers.

- **Impact**: 5-10x smaller transfers
- Reduces bandwidth usage

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

   # At application exit
   vlr.fetcher.close_connections()

Batch Requests
~~~~~~~~~~~~~~

Minimize API calls by batching operations:

.. code-block:: python

   # Good: Single call for multiple items
   matches = vlr.matches.upcoming(limit=20)
   
   # Avoid: Multiple small calls
   # matches1 = vlr.matches.upcoming(limit=5)
   # matches2 = vlr.matches.upcoming(limit=5)

Use Pagination
~~~~~~~~~~~~~~

For large datasets, use pagination instead of fetching everything:

.. code-block:: python

   # Efficient: Get specific page
   page1 = vlr.matches.completed(limit=20, page=1)
   
   # Less efficient: Fetching all at once
   # all_matches = vlr.matches.completed(limit=1000)
