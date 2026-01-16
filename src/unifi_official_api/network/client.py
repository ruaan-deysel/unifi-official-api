"""UniFi Network API client."""

from __future__ import annotations

from typing import Any

import aiohttp

from ..auth import ApiKeyAuth
from ..base import BaseUniFiClient
from ..const import DEFAULT_CONNECT_TIMEOUT, DEFAULT_TIMEOUT, NETWORK_API_BASE_URL
from .endpoints import (
    ClientsEndpoint,
    DevicesEndpoint,
    FirewallEndpoint,
    NetworksEndpoint,
    SitesEndpoint,
    WifiEndpoint,
)


class UniFiNetworkClient(BaseUniFiClient):
    """Async client for the UniFi Network API.

    This client provides access to the official UniFi Network API for managing
    network devices, clients, networks, WiFi configurations, and more.

    Example:
        ```python
        from unifi_official_api import ApiKeyAuth
        from unifi_official_api.network import UniFiNetworkClient

        async with UniFiNetworkClient(
            auth=ApiKeyAuth(api_key="your-api-key"),
        ) as client:
            # List all sites
            sites = await client.sites.list(host_id="your-host-id")

            # List devices
            devices = await client.devices.list(host_id="your-host-id")
        ```
    """

    def __init__(
        self,
        auth: ApiKeyAuth,
        *,
        base_url: str = NETWORK_API_BASE_URL,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        """Initialize the UniFi Network client.

        Args:
            auth: API key authentication.
            base_url: Base URL for the API. Defaults to the official API URL.
            session: Optional aiohttp session to reuse.
            timeout: Request timeout in seconds.
            connect_timeout: Connection timeout in seconds.
        """
        super().__init__(
            auth=auth,
            base_url=base_url,
            session=session,
            timeout=timeout,
            connect_timeout=connect_timeout,
        )

        # Initialize endpoints
        self._devices = DevicesEndpoint(self)
        self._clients = ClientsEndpoint(self)
        self._networks = NetworksEndpoint(self)
        self._wifi = WifiEndpoint(self)
        self._sites = SitesEndpoint(self)
        self._firewall = FirewallEndpoint(self)

    @property
    def devices(self) -> DevicesEndpoint:
        """Access device management endpoints."""
        return self._devices

    @property
    def clients(self) -> ClientsEndpoint:
        """Access client management endpoints."""
        return self._clients

    @property
    def networks(self) -> NetworksEndpoint:
        """Access network configuration endpoints."""
        return self._networks

    @property
    def wifi(self) -> WifiEndpoint:
        """Access WiFi configuration endpoints."""
        return self._wifi

    @property
    def sites(self) -> SitesEndpoint:
        """Access site management endpoints."""
        return self._sites

    @property
    def firewall(self) -> FirewallEndpoint:
        """Access firewall management endpoints."""
        return self._firewall

    async def validate_connection(self) -> bool:
        """Validate the connection to the UniFi Network API.

        Makes a simple API call to verify authentication and connectivity.

        Returns:
            True if the connection is valid.

        Raises:
            UniFiAuthenticationError: If authentication fails.
            UniFiConnectionError: If connection fails.
        """
        # Try to get hosts list to validate connection
        response = await self._get("/ea/hosts")
        return response is not None

    async def get_hosts(self) -> list[dict[str, Any]]:
        """Get list of available hosts.

        Returns:
            List of host information dictionaries.
        """
        response = await self._get("/ea/hosts")
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return data
        return []
