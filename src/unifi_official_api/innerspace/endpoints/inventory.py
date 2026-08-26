"""Inventory endpoint for UniFi InnerSpace API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.inventory import InventoryDevice

if TYPE_CHECKING:
    from ..client import UniFiInnerSpaceClient


class InventoryEndpoint:
    """Endpoint for retrieving unplaced hardware device inventory in UniFi InnerSpace."""

    def __init__(self, client: UniFiInnerSpaceClient) -> None:
        """
        Initialize the inventory endpoint.

        Args:
            client: The UniFi InnerSpace client.
        """
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[InventoryDevice]:
        """
        List unplaced device inventory.

        Args:
            site_id: Optional site ID filter.

        Returns:
            List of unplaced devices.
        """
        path = self._client.build_api_path("/inventory")
        params: dict[str, Any] = {}
        if site_id:
            params["siteId"] = site_id
        response = await self._client._get(path, params=params if params else None)
        if response is None:
            return []
        if isinstance(response, dict):
            devs = response.get("devices", response.get("data", []))
            if isinstance(devs, list):
                return [InventoryDevice.model_validate(item) for item in devs]
        return []
