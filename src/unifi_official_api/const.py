"""Constants for the UniFi Official API library."""

from __future__ import annotations

from typing import Final

# API Base URLs
NETWORK_API_BASE_URL: Final[str] = "https://api.ui.com"
PROTECT_API_BASE_URL: Final[str] = "https://api.ui.com"

# API Versions
NETWORK_API_VERSION: Final[str] = "v1"
PROTECT_API_VERSION: Final[str] = "v1"

# Default timeouts (in seconds)
DEFAULT_TIMEOUT: Final[int] = 30
DEFAULT_CONNECT_TIMEOUT: Final[int] = 10

# Rate limiting
DEFAULT_RATE_LIMIT_RETRY_AFTER: Final[int] = 60

# User agent
LIBRARY_VERSION: Final[str] = "0.1.0"
USER_AGENT: Final[str] = f"unifi-official-api/{LIBRARY_VERSION}"

# HTTP Headers
HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
HEADER_ACCEPT: Final[str] = "Accept"
HEADER_USER_AGENT: Final[str] = "User-Agent"
HEADER_API_KEY: Final[str] = "X-API-Key"

# Content types
CONTENT_TYPE_JSON: Final[str] = "application/json"
