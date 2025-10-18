"""Constants used throughout the library."""

VLR_BASE = "https://www.vlr.gg"
DEFAULT_TIMEOUT = 5.0
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0

# Rate limiting settings
DEFAULT_RATE_LIMIT = 10  # requests per second
DEFAULT_RATE_LIMIT_ENABLED = True
