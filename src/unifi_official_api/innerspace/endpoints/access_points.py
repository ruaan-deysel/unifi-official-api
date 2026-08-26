"""Access points endpoint for UniFi InnerSpace API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.access_point import InnerSpaceAccessPoint

if TYPE_CHECKING:
    from ..client import UniFiInnerSpaceClient


class AccessPointsEndpoint:
    """Endpoint for retrieving UniFi InnerSpace placed access points."""

    def __init__(self, client: UniFiInnerSpaceClient) -> None:
        """
        Initialize the access points endpoint.

        Args:
            client: The UniFi InnerSpace client.
        """
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[InnerSpaceAccessPoint]:
        """
        List placed access points.

        Args:
            site_id: Optional site ID filter.

        Returns:
            List of placed access points.
        """
        path = self._client.build_api_path("/access_points")
        params: dict[str, Any] = {}
        if site_id:
            params["siteId"] = site_id
        response = await self._client._get(path, params=params if params else None)
        if response is None:
            return []
        if isinstance(response, dict):
            aps = response.get("access_points", response.get("data", []))
            if isinstance(aps, list):
                return [InnerSpaceAccessPoint.model_validate(item) for item in aps]
        return []
