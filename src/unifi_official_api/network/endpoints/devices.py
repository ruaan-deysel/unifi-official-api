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

    async def get_all(
        self,
        site_id: str,
        *,
        offset: int | None = None,
        limit: int | None = None,
        filter_str: str | None = None,
    ) -> list[Device]:
        """List all adopted devices on a site.

        Args:
            site_id: The site ID.
            offset: Number of devices to skip (pagination).
            limit: Maximum number of devices to return.
            filter_str: Filter string for device properties.

        Returns:
            List of devices.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if filter_str:
            params["filter"] = filter_str

        path = self._client.build_api_path(f"/sites/{site_id}/devices")
        response = await self._client._get(path, params=params if params else None)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Device.model_validate(item) for item in data]
        return []

    async def get(self, site_id: str, device_id: str) -> Device:
        """Get a specific device.

        Args:
            site_id: The site ID.
            device_id: The device ID.

        Returns:
            The device.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/devices/{device_id}")
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Device.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Device.model_validate(data[0])
        raise ValueError(f"Device {device_id} not found")

    async def restart(self, site_id: str, device_id: str) -> bool:
        """Restart a device.

        Args:
            site_id: The site ID.
            device_id: The device ID.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/devices/{device_id}/restart")
        await self._client._post(path)
        return True

    async def adopt(
        self,
        site_id: str,
        mac: str,
    ) -> bool:
        """Adopt a device.

        Args:
            site_id: The site ID.
            mac: The device MAC address.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/devices/adopt")
        await self._client._post(path, json_data={"macAddress": mac})
        return True

    async def forget(self, site_id: str, device_id: str) -> bool:
        """Forget/remove a device.

        Args:
            site_id: The site ID.
            device_id: The device ID.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/devices/{device_id}")
        await self._client._delete(path)
        return True

    async def locate(self, site_id: str, device_id: str, enabled: bool = True) -> bool:
        """Enable or disable locate mode (LED blinking) on a device.

        Args:
            site_id: The site ID.
            device_id: The device ID.
            enabled: Whether to enable or disable locate mode.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/devices/{device_id}/locate")
        await self._client._post(path, json_data={"enabled": enabled})
        return True

    async def get_pending_adoption(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        filter_str: str | None = None,
    ) -> list[Device]:
        """List devices pending adoption.

        Args:
            offset: Number of devices to skip (pagination).
            limit: Maximum number of devices to return.
            filter_str: Filter string for device properties.

        Returns:
            List of devices pending adoption.
        """
        params: dict[str, Any] = {}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        if filter_str:
            params["filter"] = filter_str

        path = self._client.build_api_path("/pending-devices")
        response = await self._client._get(path, params=params if params else None)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Device.model_validate(item) for item in data]
        return []

    async def get_statistics(
        self,
        site_id: str,
        device_id: str,
    ) -> dict[str, Any]:
        """Get latest device statistics.

        Args:
            site_id: The site ID.
            device_id: The device ID.

        Returns:
            Device statistics dictionary.
        """
        path = self._client.build_api_path(
            f"/sites/{site_id}/devices/{device_id}/statistics/latest"
        )
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return data
        return {}

    async def execute_port_action(
        self,
        site_id: str,
        device_id: str,
        port_idx: int,
        *,
        poe_mode: str | None = None,
        speed: str | None = None,
        enabled: bool | None = None,
    ) -> bool:
        """Execute an action on a device port.

        Args:
            site_id: The site ID.
            device_id: The device ID.
            port_idx: The port index (0-based).
            poe_mode: PoE mode (off, auto, passive24, passthrough).
            speed: Port speed (auto, 10, 100, 1000, 2500, 10000).
            enabled: Whether the port is enabled.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/devices/{device_id}/ports/{port_idx}")
        data: dict[str, Any] = {}
        if poe_mode is not None:
            data["poeMode"] = poe_mode
        if speed is not None:
            data["speed"] = speed
        if enabled is not None:
            data["enabled"] = enabled

        if not data:
            raise ValueError("At least one port setting must be provided")

        await self._client._patch(path, json_data=data)
        return True

    async def execute_action(
        self,
        site_id: str,
        device_id: str,
        action: str,
    ) -> bool:
        """Execute an action on a device.

        Args:
            site_id: The site ID.
            device_id: The device ID.
            action: The action to execute (restart, locate, provision, upgrade).

        Returns:
            True if successful.
        """
        valid_actions = {"restart", "locate", "provision", "upgrade"}
        if action not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")

        path = self._client.build_api_path(f"/sites/{site_id}/devices/{device_id}/{action}")
        await self._client._post(path)
        return True
