"""Viewers endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.viewer import Viewer

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class ViewersEndpoint:
    """Endpoint for managing UniFi Protect viewers."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """Initialize the viewers endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def get_all(self, host_id: str, site_id: str) -> list[Viewer]:
        """List all viewers.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            List of viewers.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/viewers"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Viewer.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, viewer_id: str) -> Viewer:
        """Get a specific viewer.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            viewer_id: The viewer ID.

        Returns:
            The viewer.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/viewers/{viewer_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Viewer.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Viewer.model_validate(data[0])
        raise ValueError(f"Viewer {viewer_id} not found")

    async def update(
        self,
        host_id: str,
        site_id: str,
        viewer_id: str,
        **kwargs: Any,
    ) -> Viewer:
        """Update viewer settings.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            viewer_id: The viewer ID.
            **kwargs: Settings to update (name, liveview).

        Returns:
            The updated viewer.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/viewers/{viewer_id}"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return Viewer.model_validate(result)
        raise ValueError("Failed to update viewer")

    async def set_liveview(
        self,
        host_id: str,
        site_id: str,
        viewer_id: str,
        liveview_id: str | None,
    ) -> Viewer:
        """Set the liveview for a viewer.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            viewer_id: The viewer ID.
            liveview_id: The liveview ID or None to unset.

        Returns:
            The updated viewer.
        """
        return await self.update(host_id, site_id, viewer_id, liveview=liveview_id)
