"""Networks endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Network

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class NetworksEndpoint:
    """Endpoint for managing network configurations."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the networks endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def get_all(
        self,
        host_id: str,
        site_id: str,
    ) -> list[Network]:
        """List all networks.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            List of networks.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/networks"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Network.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, network_id: str) -> Network:
        """Get a specific network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            network_id: The network ID.

        Returns:
            The network.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/networks/{network_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Network.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Network.model_validate(data[0])
        raise ValueError(f"Network {network_id} not found")

    async def create(
        self,
        host_id: str,
        site_id: str,
        *,
        name: str,
        vlan_id: int | None = None,
        subnet: str | None = None,
        dhcp_enabled: bool = True,
        **kwargs: Any,
    ) -> Network:
        """Create a new network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            name: Network name.
            vlan_id: VLAN ID.
            subnet: Network subnet (e.g., "192.168.1.0/24").
            dhcp_enabled: Whether DHCP is enabled.
            **kwargs: Additional network parameters.

        Returns:
            The created network.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/networks"
        data: dict[str, Any] = {
            "name": name,
            "dhcpEnabled": dhcp_enabled,
        }
        if vlan_id is not None:
            data["vlanId"] = vlan_id
        if subnet is not None:
            data["subnet"] = subnet
        data.update(kwargs)

        response = await self._client._post(path, json_data=data)
        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return Network.model_validate(result)
        raise ValueError("Failed to create network")

    async def update(
        self,
        host_id: str,
        site_id: str,
        network_id: str,
        **kwargs: Any,
    ) -> Network:
        """Update a network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            network_id: The network ID.
            **kwargs: Network parameters to update.

        Returns:
            The updated network.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/networks/{network_id}"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return Network.model_validate(result)
        raise ValueError("Failed to update network")

    async def delete(self, host_id: str, site_id: str, network_id: str) -> bool:
        """Delete a network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            network_id: The network ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/networks/{network_id}"
        await self._client._delete(path)
        return True
