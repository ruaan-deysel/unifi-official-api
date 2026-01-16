"""WiFi endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import WifiNetwork, WifiSecurity

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class WifiEndpoint:
    """Endpoint for managing WiFi configurations."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the WiFi endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def get_all(
        self,
        host_id: str,
        site_id: str,
    ) -> list[WifiNetwork]:
        """List all WiFi networks.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            List of WiFi networks.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/wifi"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [WifiNetwork.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, wifi_id: str) -> WifiNetwork:
        """Get a specific WiFi network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            wifi_id: The WiFi network ID.

        Returns:
            The WiFi network.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/wifi/{wifi_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return WifiNetwork.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return WifiNetwork.model_validate(data[0])
        raise ValueError(f"WiFi network {wifi_id} not found")

    async def create(
        self,
        host_id: str,
        site_id: str,
        *,
        name: str,
        ssid: str,
        passphrase: str | None = None,
        security: WifiSecurity = WifiSecurity.WPA2,
        network_id: str | None = None,
        hidden: bool = False,
        **kwargs: Any,
    ) -> WifiNetwork:
        """Create a new WiFi network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            name: WiFi network name.
            ssid: The SSID to broadcast.
            passphrase: WiFi password (required for secured networks).
            security: Security type.
            network_id: Associated network ID.
            hidden: Whether to hide the SSID.
            **kwargs: Additional parameters.

        Returns:
            The created WiFi network.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/wifi"
        data: dict[str, Any] = {
            "name": name,
            "ssid": ssid,
            "security": security.value,
            "hidden": hidden,
        }
        if passphrase is not None:
            data["passphrase"] = passphrase
        if network_id is not None:
            data["networkId"] = network_id
        data.update(kwargs)

        response = await self._client._post(path, json_data=data)
        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return WifiNetwork.model_validate(result)
        raise ValueError("Failed to create WiFi network")

    async def update(
        self,
        host_id: str,
        site_id: str,
        wifi_id: str,
        **kwargs: Any,
    ) -> WifiNetwork:
        """Update a WiFi network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            wifi_id: The WiFi network ID.
            **kwargs: Parameters to update.

        Returns:
            The updated WiFi network.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/wifi/{wifi_id}"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return WifiNetwork.model_validate(result)
        raise ValueError("Failed to update WiFi network")

    async def delete(self, host_id: str, site_id: str, wifi_id: str) -> bool:
        """Delete a WiFi network.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            wifi_id: The WiFi network ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/wifi/{wifi_id}"
        await self._client._delete(path)
        return True
