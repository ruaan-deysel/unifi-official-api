"""UniFi Carrier Fabric API client."""

from __future__ import annotations

import aiohttp

from ..auth import ApiKeyAuth
from ..base import BaseUniFiClient
from ..const import (
    CARRIER_FABRIC_API_BASE_URL,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
)
from .endpoints import (
    ServicePlansEndpoint,
    SubscribersEndpoint,
)


class UniFiCarrierFabricClient(BaseUniFiClient):
    """
    Async client for the UniFi Carrier Fabric / ISP Subscriber API (api.ui.com).

    Provides subscriber lifecycle provisioning, gateway host attachment/linking,
    bandwidth service plans, and subscription state controls.
    """

    def __init__(
        self,
        auth: ApiKeyAuth,
        *,
        base_url: str = CARRIER_FABRIC_API_BASE_URL,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        """
        Initialize the UniFi Carrier Fabric client.

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
        self._subscribers = SubscribersEndpoint(self)
        self._service_plans = ServicePlansEndpoint(self)

    @property
    def subscribers(self) -> SubscribersEndpoint:
        """Access subscriber lifecycle endpoints."""
        return self._subscribers

    @property
    def service_plans(self) -> ServicePlansEndpoint:
        """Access bandwidth service plan endpoints."""
        return self._service_plans

    async def validate_connection(self) -> bool:
        """
        Validate authentication with api.ui.com.

        Returns:
            True if connection and API key are valid.
        """
        response = await self._get("/v1/carrier/service-plans")
        return response is not None
