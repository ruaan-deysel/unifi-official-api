"""NVR endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import NVR

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class NVREndpoint:
    """Endpoint for managing UniFi Protect NVR."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """Initialize the NVR endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def get(self, host_id: str, site_id: str) -> NVR:
        """Get NVR information.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            The NVR information.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/nvr"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return NVR.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return NVR.model_validate(data[0])
        raise ValueError("NVR not found")

    async def update(
        self,
        host_id: str,
        site_id: str,
        **kwargs: Any,
    ) -> NVR:
        """Update NVR settings.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            **kwargs: Settings to update.

        Returns:
            The updated NVR.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/nvr"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return NVR.model_validate(result)
        raise ValueError("Failed to update NVR")

    async def restart(self, host_id: str, site_id: str) -> bool:
        """Restart the NVR.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/nvr/restart"
        await self._client._post(path)
        return True

    async def set_recording_retention(
        self,
        host_id: str,
        site_id: str,
        days: int,
    ) -> NVR:
        """Set recording retention period.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            days: Number of days to retain recordings.

        Returns:
            The updated NVR.
        """
        if days < 1:
            raise ValueError("Retention days must be at least 1")
        return await self.update(host_id, site_id, recordingRetentionDays=days)
