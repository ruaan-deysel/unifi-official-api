"""Sensors endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Sensor

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class SensorsEndpoint:
    """Endpoint for managing UniFi Protect sensors."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """Initialize the sensors endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def get_all(self, host_id: str, site_id: str) -> list[Sensor]:
        """List all sensors.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            List of sensors.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/sensors"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Sensor.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, sensor_id: str) -> Sensor:
        """Get a specific sensor.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            sensor_id: The sensor ID.

        Returns:
            The sensor.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/sensors/{sensor_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Sensor.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Sensor.model_validate(data[0])
        raise ValueError(f"Sensor {sensor_id} not found")

    async def update(
        self,
        host_id: str,
        site_id: str,
        sensor_id: str,
        **kwargs: Any,
    ) -> Sensor:
        """Update sensor settings.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            sensor_id: The sensor ID.
            **kwargs: Settings to update.

        Returns:
            The updated sensor.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/sensors/{sensor_id}"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return Sensor.model_validate(result)
        raise ValueError("Failed to update sensor")

    async def set_status_led(
        self,
        host_id: str,
        site_id: str,
        sensor_id: str,
        enabled: bool,
    ) -> Sensor:
        """Enable or disable the status LED.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            sensor_id: The sensor ID.
            enabled: Whether to enable the LED.

        Returns:
            The updated sensor.
        """
        return await self.update(host_id, site_id, sensor_id, openStatusLedEnabled=enabled)

    async def set_motion_sensitivity(
        self,
        host_id: str,
        site_id: str,
        sensor_id: str,
        sensitivity: int,
    ) -> Sensor:
        """Set motion sensitivity.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            sensor_id: The sensor ID.
            sensitivity: Sensitivity level (0-100).

        Returns:
            The updated sensor.
        """
        if not 0 <= sensitivity <= 100:
            raise ValueError("Sensitivity must be between 0 and 100")
        return await self.update(host_id, site_id, sensor_id, motionSensitivity=sensitivity)
