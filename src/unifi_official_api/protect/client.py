"""UniFi Protect API client."""

from __future__ import annotations

from typing import Any

import aiohttp

from ..auth import ApiKeyAuth, LocalAuth
from ..base import BaseUniFiClient
from ..const import DEFAULT_CONNECT_TIMEOUT, DEFAULT_TIMEOUT, PROTECT_API_BASE_URL
from ..exceptions import UniFiConnectionError, UniFiTimeoutError
from .endpoints import (
    CamerasEndpoint,
    ChimesEndpoint,
    EventsEndpoint,
    LightsEndpoint,
    LiveViewsEndpoint,
    NVREndpoint,
    SensorsEndpoint,
)


class UniFiProtectClient(BaseUniFiClient):
    """Async client for the UniFi Protect API.

    This client provides access to the official UniFi Protect API for managing
    cameras, sensors, lights, chimes, and NVR settings.

    Example:
        ```python
        from unifi_official_api import ApiKeyAuth
        from unifi_official_api.protect import UniFiProtectClient

        async with UniFiProtectClient(
            auth=ApiKeyAuth(api_key="your-api-key"),
        ) as client:
            # List all cameras
            cameras = await client.cameras.list(
                host_id="your-host-id",
                site_id="your-site-id"
            )

            # Get snapshot from a camera
            snapshot = await client.cameras.get_snapshot(
                host_id="your-host-id",
                site_id="your-site-id",
                camera_id="camera-id"
            )
        ```
    """

    def __init__(
        self,
        auth: ApiKeyAuth | LocalAuth,
        *,
        base_url: str = PROTECT_API_BASE_URL,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        """Initialize the UniFi Protect client.

        Args:
            auth: API key or local authentication.
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
        self._cameras = CamerasEndpoint(self)
        self._sensors = SensorsEndpoint(self)
        self._lights = LightsEndpoint(self)
        self._chimes = ChimesEndpoint(self)
        self._nvr = NVREndpoint(self)
        self._liveviews = LiveViewsEndpoint(self)
        self._events = EventsEndpoint(self)

    @property
    def cameras(self) -> CamerasEndpoint:
        """Access camera management endpoints."""
        return self._cameras

    @property
    def sensors(self) -> SensorsEndpoint:
        """Access sensor management endpoints."""
        return self._sensors

    @property
    def lights(self) -> LightsEndpoint:
        """Access light management endpoints."""
        return self._lights

    @property
    def chimes(self) -> ChimesEndpoint:
        """Access chime management endpoints."""
        return self._chimes

    @property
    def nvr(self) -> NVREndpoint:
        """Access NVR management endpoints."""
        return self._nvr

    @property
    def liveviews(self) -> LiveViewsEndpoint:
        """Access live view management endpoints."""
        return self._liveviews

    @property
    def events(self) -> EventsEndpoint:
        """Access event management endpoints."""
        return self._events

    async def validate_connection(self) -> bool:
        """Validate the connection to the UniFi Protect API.

        Makes a simple API call to verify authentication and connectivity.

        Returns:
            True if the connection is valid.

        Raises:
            UniFiAuthenticationError: If authentication fails.
            UniFiConnectionError: If connection fails.
        """
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

    async def _get_binary(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Make a GET request that returns binary data.

        Args:
            path: API path.
            params: Query parameters.

        Returns:
            Binary response data.

        Raises:
            UniFiConnectionError: If connection fails.
            UniFiTimeoutError: If request times out.
        """

        session = await self._ensure_session()
        url = self._build_url(path)
        headers = self._get_headers()
        # Remove JSON content type for binary requests
        headers.pop("Content-Type", None)
        headers["Accept"] = "*/*"

        try:
            async with session.get(
                url,
                params=params,
                headers=headers,
            ) as response:
                if response.status >= 400:
                    text = await response.text()
                    raise UniFiConnectionError(
                        f"Failed to fetch binary data: {response.status} - {text}"
                    )
                return await response.read()

        except aiohttp.ClientConnectorError as err:
            raise UniFiConnectionError(
                f"Failed to connect to {url}: {err}"
            ) from err
        except TimeoutError as err:
            raise UniFiTimeoutError(
                f"Request to {url} timed out"
            ) from err
        except aiohttp.ClientError as err:
            raise UniFiConnectionError(
                f"Request to {url} failed: {err}"
            ) from err
