Rate Limiting
==============

The vlrdevapi library includes built-in rate limiting to prevent overloading VLR.gg servers and to avoid getting blocked.

Default Configuration
---------------------

By default, the library limits requests to **10 requests per second**. This applies to:

- Individual requests via ``fetch_html()``
- Concurrent requests via ``batch_fetch_html()``
- All API endpoints (matches, events, teams, players, etc.)

The rate limiter uses a sliding window algorithm that tracks recent request timestamps and automatically throttles requests when the limit is reached.

Configuring Rate Limits
------------------------

You can adjust the rate limit to suit your needs:

.. code-block:: python

   # docs-validate: skip
   import vlrdevapi as vlr

   # Check current rate limit (0.0 means disabled)
   current = vlr.get_rate_limit()
   print(f"Current: {current} requests/second")

   # Increase to 20 requests/second (enabled)
   vlr.configure_rate_limit(requests_per_second=20.0, enabled=True)

   # Decrease to 5 requests/second (more conservative)
   vlr.configure_rate_limit(requests_per_second=5.0, enabled=True)

   # Disable rate limiting (NOT recommended)
   vlr.configure_rate_limit(enabled=False)

   # Restore defaults (10 req/s, enabled)
   vlr.reset_rate_limit()

How It Works
------------

The rate limiter:

1. **Tracks timestamps**: Maintains a sliding window of the last 100 request timestamps
2. **Calculates rate**: Counts requests in the last 1 second
3. **Throttles automatically**: If limit is exceeded, waits until a request slot is available
4. **Thread-safe**: Works correctly with concurrent/parallel requests
5. **Transparent**: No code changes needed - works automatically

Example
-------

.. code-block:: python

   import time
   import vlrdevapi as vlr

   # Set a conservative rate limit
   vlr.configure_rate_limit(requests_per_second=2.0, enabled=True)  # 2 requests/second

   start = time.time()

   # Make 5 requests - will automatically throttle
   for i in range(5):
       info = vlr.series.info(match_id=12345 + i)
       print(f"Request {i+1} completed")

   elapsed = time.time() - start
   print(f"Total time: {elapsed:.1f}s")
   # Expected: ~2.5 seconds for 5 requests at 2 req/s

Concurrent Requests
-------------------

Rate limiting works seamlessly with batch fetching:

.. code-block:: python

   import vlrdevapi as vlr

   # Set rate limit
   vlr.configure_rate_limit(requests_per_second=10.0, enabled=True)

   # Batch fetch respects rate limit
   # Even though we use 4 workers, total rate won't exceed 10 req/s
   matches = vlr.events.matches(event_id=2498, limit=20)

Best Practices
--------------

**Recommended Settings:**

- **Default (10 req/s)**: Good for most use cases
- **Conservative (5 req/s)**: For bulk scraping or long-running scripts
- **Aggressive (20 req/s)**: Only if you need faster responses and monitor for 429 errors

**Guidelines:**

1. **Keep rate limiting enabled** - Protects both you and the server
2. **Monitor for 429 errors** - If you get rate limited, decrease your limit
3. **Lower for bulk operations** - Use 5 req/s for large datasets
4. **Test your limits** - Start conservative, increase if needed
5. **Respect the server** - VLR.gg provides free data, don't abuse it

Troubleshooting
---------------

**Getting 429 (Rate Limited) errors?**

.. code-block:: python

   # docs-validate: skip
   # Decrease your rate limit
   vlr.configure_rate_limit(requests_per_second=5.0, enabled=True)

**Requests too slow?**

.. code-block:: python

   # docs-validate: skip
   # Check current setting
   print(vlr.get_rate_limit())
   
   # Increase cautiously
   vlr.configure_rate_limit(requests_per_second=15.0, enabled=True)

**Need to bypass for testing?**

.. code-block:: python

   # docs-validate: skip
   # Disable temporarily (use with caution)
   vlr.configure_rate_limit(enabled=False)
   
   # ... your test code ...
   
   # Re-enable defaults
   vlr.reset_rate_limit()

Technical Details
-----------------

The rate limiter implementation:

- Uses ``threading.Lock`` for thread safety
- Maintains a ``deque`` of timestamps (max 100 entries)
- Calculates wait time based on oldest timestamp in the window
- Sleeps the calling thread if rate limit is exceeded
- Applies before each HTTP request in ``fetch_html_with_retry()``

This ensures consistent rate limiting across all API calls, whether sequential or concurrent.
