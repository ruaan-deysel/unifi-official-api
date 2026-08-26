"""Link Stations endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.bridge import LinkStation

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class LinkStationsEndpoint:
    """Endpoint for managing UniFi Protect link stations."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[LinkStation]:
        path = self._client.build_api_path("/link-stations", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [LinkStation.model_validate(item) for item in data]
        return []

    async def get(self, station_id: str, site_id: str | None = None) -> LinkStation:
        path = self._client.build_api_path(f"/link-stations/{station_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return LinkStation.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return LinkStation.model_validate(data[0])
        raise ValueError(f"Link station {station_id} not found")

    async def update(
        self,
        station_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> LinkStation:
        path = self._client.build_api_path(f"/link-stations/{station_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return LinkStation.model_validate(data)
        raise ValueError(f"Failed to update link station {station_id}")
