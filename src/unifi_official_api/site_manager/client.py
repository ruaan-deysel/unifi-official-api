"""UniFi Site Manager API client."""

from __future__ import annotations

import aiohttp

from ..auth import ApiKeyAuth
from ..base import BaseUniFiClient
from ..const import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
    SITE_MANAGER_API_BASE_URL,
)
from .endpoints import (
    ConnectorEndpoint,
    DevicesEndpoint,
    HostsEndpoint,
    ISPMetricsEndpoint,
    SDWanEndpoint,
    SitesEndpoint,
)


class UniFiSiteManagerClient(BaseUniFiClient):
    """
    Async client for the UniFi Site Manager API (api.ui.com).

    Provides cloud-level management of consoles/hosts, sites, device inventories,
    ISP metric telemetry, SD-WAN topologies, and Cloud Connector proxying.
    """

    def __init__(
        self,
        auth: ApiKeyAuth,
        *,
        base_url: str = SITE_MANAGER_API_BASE_URL,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        """
        Initialize the UniFi Site Manager client.

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
        self._hosts = HostsEndpoint(self)
        self._sites = SitesEndpoint(self)
        self._devices = DevicesEndpoint(self)
        self._isp_metrics = ISPMetricsEndpoint(self)
        self._sd_wan = SDWanEndpoint(self)
        self._connector = ConnectorEndpoint(self)

    @property
    def hosts(self) -> HostsEndpoint:
        """Access hosts management endpoints."""
        return self._hosts

    @property
    def sites(self) -> SitesEndpoint:
        """Access multi-site management endpoints."""
        return self._sites

    @property
    def devices(self) -> DevicesEndpoint:
        """Access cross-console device inventory endpoints."""
        return self._devices

    @property
    def isp_metrics(self) -> ISPMetricsEndpoint:
        """Access ISP WAN telemetry metrics endpoints."""
        return self._isp_metrics

    @property
    def sd_wan(self) -> SDWanEndpoint:
        """Access SD-WAN configuration and status endpoints."""
        return self._sd_wan

    @property
    def connector(self) -> ConnectorEndpoint:
        """Access Site Manager Cloud Connector proxy endpoint."""
        return self._connector

    async def validate_connection(self) -> bool:
        """
        Validate authentication with api.ui.com.

        Returns:
            True if connection and API key are valid.
        """
        response = await self._get("/v1/hosts", params={"limit": 1})
        return response is not None
