"""UniFi InnerSpace API client."""

from __future__ import annotations

from typing import Any

import aiohttp

from ..auth import ApiKeyAuth, LocalAuth
from ..base import BaseUniFiClient
from ..const import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
    INNERSPACE_API_BASE_URL,
    INNERSPACE_INTEGRATION_PATH,
    ConnectionType,
)
from ..exceptions import UniFiConnectionError, UniFiTimeoutError
from .endpoints import (
    AccessPointsEndpoint,
    AssetsEndpoint,
    FloorPlansEndpoint,
    InventoryEndpoint,
    ProjectEndpoint,
    SwitchesEndpoint,
)


class UniFiInnerSpaceClient(BaseUniFiClient):
    """
    Async client for the UniFi InnerSpace API.

    Provides access to floor plans, RF coverage geometry, placed access points,
    switches, hardware inventory, and blueprint assets.
    """

    def __init__(
        self,
        auth: ApiKeyAuth | LocalAuth,
        *,
        base_url: str | None = None,
        connection_type: ConnectionType = ConnectionType.LOCAL,
        console_id: str | None = None,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        """
        Initialize the UniFi InnerSpace client.

        Args:
            auth: API key authentication (ApiKeyAuth or LocalAuth).
            base_url: Base URL (required for LOCAL, defaults to api.ui.com for REMOTE).
            connection_type: Connection type (LOCAL or REMOTE).
            console_id: Console ID for REMOTE connections.
            session: Optional aiohttp session.
            timeout: Request timeout in seconds.
            connect_timeout: Connection timeout in seconds.
        """
        if base_url is None:
            if connection_type == ConnectionType.REMOTE:
                base_url = INNERSPACE_API_BASE_URL
            else:
                raise ValueError("base_url is required for LOCAL connection type")

        if connection_type == ConnectionType.REMOTE and not console_id:
            raise ValueError("console_id is required for REMOTE connection type")

        super().__init__(
            auth=auth,
            base_url=base_url,
            session=session,
            timeout=timeout,
            connect_timeout=connect_timeout,
        )

        self._connection_type = connection_type
        self._console_id = console_id

        # Initialize endpoints
        self._project = ProjectEndpoint(self)
        self._floor_plans = FloorPlansEndpoint(self)
        self._access_points = AccessPointsEndpoint(self)
        self._switches = SwitchesEndpoint(self)
        self._inventory = InventoryEndpoint(self)
        self._assets = AssetsEndpoint(self)

    @property
    def connection_type(self) -> ConnectionType:
        """Return the connection type."""
        return self._connection_type

    @property
    def console_id(self) -> str | None:
        """Return the console ID (for REMOTE connections)."""
        return self._console_id

    def build_api_path(self, endpoint: str) -> str:
        """
        Build the full API path based on connection type.

        Args:
            endpoint: API endpoint (e.g., "/floor_plans").

        Returns:
            Full API path.
        """
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        if self._connection_type == ConnectionType.LOCAL:
            return f"{INNERSPACE_INTEGRATION_PATH}{endpoint}"

        connector_path = INNERSPACE_INTEGRATION_PATH.removeprefix("/proxy")
        return f"/v1/connector/consoles/{self._console_id}{connector_path}{endpoint}"

    @property
    def project(self) -> ProjectEndpoint:
        """Access project data endpoint."""
        return self._project

    @property
    def floor_plans(self) -> FloorPlansEndpoint:
        """Access floor plans endpoints."""
        return self._floor_plans

    @property
    def access_points(self) -> AccessPointsEndpoint:
        """Access placed access points endpoints."""
        return self._access_points

    @property
    def switches(self) -> SwitchesEndpoint:
        """Access placed switches endpoints."""
        return self._switches

    @property
    def inventory(self) -> InventoryEndpoint:
        """Access hardware inventory endpoints."""
        return self._inventory

    @property
    def assets(self) -> AssetsEndpoint:
        """Access floor plan blueprint asset endpoints."""
        return self._assets

    async def validate_connection(self) -> bool:
        """
        Validate the connection to the InnerSpace API.

        Returns:
            True if connection is valid.
        """
        response = await self._get(self.build_api_path("/floor_plans"))
        return response is not None

    async def get_binary(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Download binary data from an endpoint path.

        Args:
            path: Relative API path.
            params: Optional query params.

        Returns:
            Raw response bytes.
        """
        session = await self._ensure_session()
        url = self._build_url(path)
        headers = self._get_headers()
        headers.pop("Content-Type", None)
        headers["Accept"] = "*/*"

        try:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status >= 400:
                    raise UniFiConnectionError(
                        f"Failed to fetch binary asset: HTTP {response.status}"
                    )
                return await response.read()
        except TimeoutError as err:
            raise UniFiTimeoutError(f"Request to {url} timed out") from err
        except aiohttp.ClientError as err:
            raise UniFiConnectionError(f"Request to {url} failed: {err}") from err
