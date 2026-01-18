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
        site_id: str,
        *,
        offset: int | None = None,
        limit: int | None = None,
        filter_str: str | None = None,
    ) -> list[WifiNetwork]:
        """List all WiFi networks.

        Args:
            site_id: The site ID.
            offset: Number of WiFi networks to skip (pagination).
            limit: Maximum number of WiFi networks to return.
            filter_str: Filter string for WiFi properties.

        Returns:
            List of WiFi networks.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if filter_str:
            params["filter"] = filter_str

        path = self._client.build_api_path(f"/sites/{site_id}/wifi/broadcasts")
        response = await self._client._get(path, params=params if params else None)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [WifiNetwork.model_validate(item) for item in data]
        return []

    async def get(self, site_id: str, wifi_id: str) -> WifiNetwork:
        """Get a specific WiFi network.

        Args:
            site_id: The site ID.
            wifi_id: The WiFi network ID.

        Returns:
            The WiFi network.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/wifi/broadcasts/{wifi_id}")
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
        path = self._client.build_api_path(f"/sites/{site_id}/wifi/broadcasts")
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
        site_id: str,
        wifi_id: str,
        **kwargs: Any,
    ) -> WifiNetwork:
        """Update a WiFi network.

        Args:
            site_id: The site ID.
            wifi_id: The WiFi network ID.
            **kwargs: Parameters to update.

        Returns:
            The updated WiFi network.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/wifi/broadcasts/{wifi_id}")
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return WifiNetwork.model_validate(result)
        raise ValueError("Failed to update WiFi network")

    async def delete(self, site_id: str, wifi_id: str) -> bool:
        """Delete a WiFi network.

        Args:
            site_id: The site ID.
            wifi_id: The WiFi network ID.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/wifi/broadcasts/{wifi_id}")
        await self._client._delete(path)
        return True
