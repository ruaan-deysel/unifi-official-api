"""Bridges endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.bridge import Bridge

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class BridgesEndpoint:
    """Endpoint for managing UniFi Protect bridges."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[Bridge]:
        path = self._client.build_api_path("/bridges", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Bridge.model_validate(item) for item in data]
        return []

    async def get(self, bridge_id: str, site_id: str | None = None) -> Bridge:
        path = self._client.build_api_path(f"/bridges/{bridge_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Bridge.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return Bridge.model_validate(data[0])
        raise ValueError(f"Bridge {bridge_id} not found")

    async def update(
        self,
        bridge_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> Bridge:
        path = self._client.build_api_path(f"/bridges/{bridge_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Bridge.model_validate(data)
        raise ValueError(f"Failed to update bridge {bridge_id}")
