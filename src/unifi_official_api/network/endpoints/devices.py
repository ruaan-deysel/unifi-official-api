"""Devices endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Device

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class DevicesEndpoint:
    """Endpoint for managing UniFi network devices."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the devices endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def list(
        self,
        host_id: str,
        site_id: str | None = None,
    ) -> list[Device]:
        """List all devices.

        Args:
            host_id: The host ID.
            site_id: Optional site ID to filter by.

        Returns:
            List of devices.
        """
        params: dict[str, Any] = {}
        if site_id:
            params["siteId"] = site_id

        path = f"/ea/hosts/{host_id}/devices"
        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Device.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, device_id: str) -> Device:
        """Get a specific device.

        Args:
            host_id: The host ID.
            device_id: The device ID.

        Returns:
            The device.
        """
        path = f"/ea/hosts/{host_id}/devices/{device_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Device.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Device.model_validate(data[0])
        raise ValueError(f"Device {device_id} not found")

    async def restart(self, host_id: str, device_id: str) -> bool:
        """Restart a device.

        Args:
            host_id: The host ID.
            device_id: The device ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/devices/{device_id}/restart"
        await self._client._post(path)
        return True

    async def adopt(
        self,
        host_id: str,
        site_id: str,
        mac: str,
    ) -> bool:
        """Adopt a device.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            mac: The device MAC address.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/devices/adopt"
        await self._client._post(path, json_data={"mac": mac})
        return True

    async def forget(self, host_id: str, device_id: str) -> bool:
        """Forget/remove a device.

        Args:
            host_id: The host ID.
            device_id: The device ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/devices/{device_id}"
        await self._client._delete(path)
        return True
