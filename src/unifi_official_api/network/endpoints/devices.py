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

    async def locate(self, host_id: str, device_id: str, enabled: bool = True) -> bool:
        """Enable or disable locate mode (LED blinking) on a device.

        Args:
            host_id: The host ID.
            device_id: The device ID.
            enabled: Whether to enable or disable locate mode.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/devices/{device_id}/locate"
        await self._client._post(path, json_data={"enabled": enabled})
        return True

    async def get_pending_adoption(self, host_id: str) -> list[Device]:
        """List devices pending adoption.

        Args:
            host_id: The host ID.

        Returns:
            List of devices pending adoption.
        """
        path = f"/ea/hosts/{host_id}/devices/pending-adoption"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Device.model_validate(item) for item in data]
        return []

    async def get_statistics(
        self,
        host_id: str,
        device_id: str,
    ) -> dict[str, Any]:
        """Get latest device statistics.

        Args:
            host_id: The host ID.
            device_id: The device ID.

        Returns:
            Device statistics dictionary.
        """
        path = f"/ea/hosts/{host_id}/devices/{device_id}/statistics/latest"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return data
        return {}

    async def execute_port_action(
        self,
        host_id: str,
        device_id: str,
        port_idx: int,
        *,
        poe_mode: str | None = None,
        speed: str | None = None,
        enabled: bool | None = None,
    ) -> bool:
        """Execute an action on a device port.

        Args:
            host_id: The host ID.
            device_id: The device ID.
            port_idx: The port index (1-based).
            poe_mode: PoE mode (off, auto, passive24, passthrough).
            speed: Port speed (auto, 10, 100, 1000, 2500, 10000).
            enabled: Whether the port is enabled.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/devices/{device_id}/ports/{port_idx}"
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
        host_id: str,
        device_id: str,
        action: str,
    ) -> bool:
        """Execute an action on a device.

        Args:
            host_id: The host ID.
            device_id: The device ID.
            action: The action to execute (restart, locate, provision, upgrade).

        Returns:
            True if successful.
        """
        valid_actions = {"restart", "locate", "provision", "upgrade"}
        if action not in valid_actions:
            raise ValueError(f"Action must be one of: {', '.join(valid_actions)}")

        path = f"/ea/hosts/{host_id}/devices/{device_id}/{action}"
        await self._client._post(path)
        return True
