"""UniFi Mobility API client."""

from __future__ import annotations

import aiohttp

from ..auth import ApiKeyAuth
from ..base import BaseUniFiClient
from ..const import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
    MOBILITY_API_BASE_URL,
)
from .endpoints import (
    ClientsEndpoint,
    DevicesEndpoint,
    NetworkEndpoint,
    WirelessEndpoint,
    WorkspacesEndpoint,
)


class UniFiMobilityClient(BaseUniFiClient):
    """
    Async client for the UniFi Mobility API (api.ui.com).

    Provides cloud management of mobility router gateways (UMR devices),
    workspaces, connected clients, and remote network/wireless configurations.
    """

    def __init__(
        self,
        auth: ApiKeyAuth,
        *,
        base_url: str = MOBILITY_API_BASE_URL,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        """
        Initialize the UniFi Mobility client.

        Args:
            auth: Cloud API key authentication (ApiKeyAuth).
            base_url: Base URL (defaults to https://api.ui.com).
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
        self._workspaces = WorkspacesEndpoint(self)
        self._devices = DevicesEndpoint(self)
        self._clients = ClientsEndpoint(self)
        self._network = NetworkEndpoint(self)
        self._wireless = WirelessEndpoint(self)

    @property
    def workspaces(self) -> WorkspacesEndpoint:
        """Access workspace and admin management endpoints."""
        return self._workspaces

    @property
    def devices(self) -> DevicesEndpoint:
        """Access mobility router device management endpoints."""
        return self._devices

    @property
    def clients(self) -> ClientsEndpoint:
        """Access connected client monitoring endpoints."""
        return self._clients

    @property
    def network(self) -> NetworkEndpoint:
        """Access LAN/DHCP configuration endpoints."""
        return self._network

    @property
    def wireless(self) -> WirelessEndpoint:
        """Access WiFi configuration endpoints."""
        return self._wireless

    async def validate_connection(self) -> bool:
        """
        Validate authentication with api.ui.com.

        Returns:
            True if connection and API key are valid.
        """
        response = await self._get("/v1/mobility/workspaces")
        return response is not None
