"""Supporting resources endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.resources import (
    DeviceTag,
    RADIUSProfile,
    VPNServer,
    VPNTunnel,
    WANInterface,
)

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class ResourcesEndpoint:
    """Endpoint for accessing supporting network resources."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the resources endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    # WAN Interfaces

    async def get_wan_interfaces(
        self,
        host_id: str,
        site_id: str,
        *,
        offset: int = 0,
        limit: int = 25,
    ) -> list[WANInterface]:
        """List all WAN interfaces.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of WAN interfaces.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/wan"
        params: dict[str, Any] = {"offset": offset, "limit": limit}

        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [WANInterface.model_validate(item) for item in data]
        return []

    # VPN Tunnels

    async def get_vpn_tunnels(
        self,
        host_id: str,
        site_id: str,
        *,
        offset: int = 0,
        limit: int = 25,
    ) -> list[VPNTunnel]:
        """List all site-to-site VPN tunnels.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of VPN tunnels.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/vpn/tunnels"
        params: dict[str, Any] = {"offset": offset, "limit": limit}

        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [VPNTunnel.model_validate(item) for item in data]
        return []

    # VPN Servers

    async def get_vpn_servers(
        self,
        host_id: str,
        site_id: str,
        *,
        offset: int = 0,
        limit: int = 25,
    ) -> list[VPNServer]:
        """List all VPN servers.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of VPN servers.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/vpn/servers"
        params: dict[str, Any] = {"offset": offset, "limit": limit}

        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [VPNServer.model_validate(item) for item in data]
        return []

    # RADIUS Profiles

    async def get_radius_profiles(
        self,
        host_id: str,
        site_id: str,
        *,
        offset: int = 0,
        limit: int = 25,
    ) -> list[RADIUSProfile]:
        """List all RADIUS profiles.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of RADIUS profiles.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/radius/profiles"
        params: dict[str, Any] = {"offset": offset, "limit": limit}

        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [RADIUSProfile.model_validate(item) for item in data]
        return []

    # Device Tags

    async def get_device_tags(
        self,
        host_id: str,
        site_id: str,
        *,
        offset: int = 0,
        limit: int = 25,
    ) -> list[DeviceTag]:
        """List all device tags.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            offset: Pagination offset.
            limit: Maximum results.

        Returns:
            List of device tags.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/device-tags"
        params: dict[str, Any] = {"offset": offset, "limit": limit}

        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [DeviceTag.model_validate(item) for item in data]
        return []
