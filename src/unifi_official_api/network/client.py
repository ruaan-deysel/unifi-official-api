"""UniFi Network API client."""

from __future__ import annotations

import aiohttp

from ..auth import ApiKeyAuth, LocalAuth
from ..base import BaseUniFiClient
from ..const import (
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_TIMEOUT,
    NETWORK_API_BASE_URL,
    NETWORK_INTEGRATION_PATH,
    ConnectionType,
)
from .endpoints import (
    ACLEndpoint,
    ClientsEndpoint,
    DevicesEndpoint,
    DNSEndpoint,
    FirewallEndpoint,
    NetworksEndpoint,
    ResourcesEndpoint,
    SitesEndpoint,
    TrafficEndpoint,
    VouchersEndpoint,
    WifiEndpoint,
)
from .models import ApplicationInfo


class UniFiNetworkClient(BaseUniFiClient):
    """Async client for the UniFi Network API.

    This client provides access to the official UniFi Network API for managing
    network devices, clients, networks, WiFi configurations, and more.

    Supports two connection types:
    - LOCAL: Direct connection to a UniFi console (e.g., UDM-Pro at 192.168.1.1)
    - REMOTE: Cloud connection via api.ui.com (requires cloud API key)

    Example (Local Connection):
        ```python
        from unifi_official_api import LocalAuth, ConnectionType
        from unifi_official_api.network import UniFiNetworkClient

        async with UniFiNetworkClient(
            auth=LocalAuth(api_key="your-local-api-key", verify_ssl=False),
            base_url="https://192.168.1.1",
            connection_type=ConnectionType.LOCAL,
        ) as client:
            # List all sites (no host_id needed for local)
            sites = await client.sites.get_all()

            # List devices for a site
            devices = await client.devices.get_all(site_id="default")
        ```

    Example (Remote/Cloud Connection):
        ```python
        from unifi_official_api import ApiKeyAuth, ConnectionType
        from unifi_official_api.network import UniFiNetworkClient

        async with UniFiNetworkClient(
            auth=ApiKeyAuth(api_key="your-cloud-api-key"),
            connection_type=ConnectionType.REMOTE,
            console_id="your-console-id",
        ) as client:
            # List all sites
            sites = await client.sites.get_all()

            # List devices
            devices = await client.devices.get_all(site_id="your-site-id")
        ```
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
        """Initialize the UniFi Network client.

        Args:
            auth: API key authentication (ApiKeyAuth for cloud, LocalAuth for local).
            base_url: Base URL for the API. For LOCAL, this is the console IP
                (e.g., https://192.168.1.1). For REMOTE, defaults to api.ui.com.
            connection_type: Connection type (LOCAL or REMOTE).
            console_id: Console ID for REMOTE connections (required for REMOTE).
            session: Optional aiohttp session to reuse.
            timeout: Request timeout in seconds.
            connect_timeout: Connection timeout in seconds.

        Raises:
            ValueError: If REMOTE connection type is used without console_id.
        """
        # Determine base URL
        if base_url is None:
            if connection_type == ConnectionType.REMOTE:
                base_url = NETWORK_API_BASE_URL
            else:
                raise ValueError("base_url is required for LOCAL connection type")

        # Validate console_id for REMOTE
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
        self._devices = DevicesEndpoint(self)
        self._clients = ClientsEndpoint(self)
        self._networks = NetworksEndpoint(self)
        self._wifi = WifiEndpoint(self)
        self._sites = SitesEndpoint(self)
        self._firewall = FirewallEndpoint(self)
        self._vouchers = VouchersEndpoint(self)
        self._acl = ACLEndpoint(self)
        self._traffic = TrafficEndpoint(self)
        self._resources = ResourcesEndpoint(self)
        self._dns = DNSEndpoint(self)

    @property
    def connection_type(self) -> ConnectionType:
        """Return the connection type."""
        return self._connection_type

    @property
    def console_id(self) -> str | None:
        """Return the console ID (for REMOTE connections)."""
        return self._console_id

    def build_api_path(self, endpoint: str) -> str:
        """Build the full API path based on connection type.

        Args:
            endpoint: The API endpoint path (e.g., "/sites", "/sites/{siteId}/devices").

        Returns:
            Full API path with proper prefix for the connection type.
        """
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        if self._connection_type == ConnectionType.LOCAL:
            # Local: /proxy/network/integration/v1{endpoint}
            return f"{NETWORK_INTEGRATION_PATH}{endpoint}"
        else:
            # Remote: /v1/connector/consoles/{consoleId}/proxy/network/integration/v1{endpoint}
            return f"/v1/connector/consoles/{self._console_id}{NETWORK_INTEGRATION_PATH}{endpoint}"

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

    @property
    def vouchers(self) -> VouchersEndpoint:
        """Access hotspot voucher management endpoints."""
        return self._vouchers

    @property
    def acl(self) -> ACLEndpoint:
        """Access ACL (Access Control List) rule endpoints."""
        return self._acl

    @property
    def traffic(self) -> TrafficEndpoint:
        """Access traffic matching and DPI endpoints."""
        return self._traffic

    @property
    def resources(self) -> ResourcesEndpoint:
        """Access supporting resources (WAN, VPN, RADIUS, etc)."""
        return self._resources

    @property
    def dns(self) -> DNSEndpoint:
        """Access DNS policy management endpoints."""
        return self._dns

    async def validate_connection(self) -> bool:
        """Validate the connection to the UniFi Network API.

        Makes a simple API call to verify authentication and connectivity.

        Returns:
            True if the connection is valid.

        Raises:
            UniFiAuthenticationError: If authentication fails.
            UniFiConnectionError: If connection fails.
        """
        # Try to get sites list to validate connection
        response = await self._get(self.build_api_path("/sites"))
        return response is not None

    async def get_application_info(self) -> ApplicationInfo:
        """Get UniFi Network application information.

        Returns the application version and other metadata.
        Official endpoint: GET /v1/info

        Returns:
            ApplicationInfo with the application version.

        Raises:
            ValueError: If the response cannot be parsed.
        """
        path = self.build_api_path("/info")
        response = await self._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return ApplicationInfo.model_validate(data)
        raise ValueError("Unable to retrieve application info")
