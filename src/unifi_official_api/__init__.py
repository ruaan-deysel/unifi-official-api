"""UniFi Official API - Async Python library for UniFi Network and Protect APIs.

This library provides async Python clients for the official UniFi APIs:
- UniFi Network API: Manage network devices, clients, WiFi, and more
- UniFi Protect API: Manage cameras, sensors, lights, and NVR settings

Example:
    ```python
    from unifi_official_api import ApiKeyAuth
    from unifi_official_api.network import UniFiNetworkClient
    from unifi_official_api.protect import UniFiProtectClient

    # Network API
    async with UniFiNetworkClient(
        auth=ApiKeyAuth(api_key="your-api-key"),
    ) as client:
        devices = await client.devices.list(host_id="your-host-id")

    # Protect API
    async with UniFiProtectClient(
        auth=ApiKeyAuth(api_key="your-api-key"),
    ) as client:
        cameras = await client.cameras.list(
            host_id="your-host-id",
            site_id="your-site-id"
        )
    ```
"""

from __future__ import annotations

from ._version import __version__
from .auth import ApiKeyAuth, ApiKeyType, LocalAuth
from .exceptions import (
    UniFiAuthenticationError,
    UniFiConnectionError,
    UniFiError,
    UniFiNotFoundError,
    UniFiRateLimitError,
    UniFiResponseError,
    UniFiTimeoutError,
    UniFiValidationError,
)

__all__ = [
    # Version
    "__version__",
    # Authentication
    "ApiKeyAuth",
    "ApiKeyType",
    "LocalAuth",
    # Exceptions
    "UniFiAuthenticationError",
    "UniFiConnectionError",
    "UniFiError",
    "UniFiNotFoundError",
    "UniFiRateLimitError",
    "UniFiResponseError",
    "UniFiTimeoutError",
    "UniFiValidationError",
]
