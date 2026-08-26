"""Assets endpoint for UniFi InnerSpace API."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import UniFiInnerSpaceClient


class AssetsEndpoint:
    """Endpoint for downloading floor plan assets (blueprint images) in UniFi InnerSpace."""

    def __init__(self, client: UniFiInnerSpaceClient) -> None:
        """
        Initialize the assets endpoint.

        Args:
            client: The UniFi InnerSpace client.
        """
        self._client = client

    async def download(self, plan_id: str, filename: str) -> bytes:
        """
        Download plan asset file.

        Args:
            plan_id: Floor plan ID.
            filename: Asset filename.

        Returns:
            Binary file content bytes.
        """
        path = self._client.build_api_path(f"/assets/{plan_id}/{filename}")
        return await self._client.get_binary(path)
