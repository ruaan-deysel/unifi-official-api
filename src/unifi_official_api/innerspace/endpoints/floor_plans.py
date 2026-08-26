"""Floor plans endpoint for UniFi InnerSpace API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.floor_plan import FloorPlan

if TYPE_CHECKING:
    from ..client import UniFiInnerSpaceClient


class FloorPlansEndpoint:
    """Endpoint for managing UniFi InnerSpace floor plans."""

    def __init__(self, client: UniFiInnerSpaceClient) -> None:
        """
        Initialize the floor plans endpoint.

        Args:
            client: The UniFi InnerSpace client.
        """
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[FloorPlan]:
        """
        List floor plans.

        Args:
            site_id: Optional site ID filter.

        Returns:
            List of floor plans.
        """
        path = self._client.build_api_path("/floor_plans")
        params: dict[str, Any] = {}
        if site_id:
            params["siteId"] = site_id
        response = await self._client._get(path, params=params if params else None)
        if response is None:
            return []
        if isinstance(response, dict):
            plans = response.get("floor_plans", response.get("data", []))
            if isinstance(plans, list):
                return [FloorPlan.model_validate(item) for item in plans]
        return []
