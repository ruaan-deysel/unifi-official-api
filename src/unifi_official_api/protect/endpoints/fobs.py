"""Fobs endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.fob import Fob

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class FobsEndpoint:
    """Endpoint for managing UniFi Protect fobs."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[Fob]:
        path = self._client.build_api_path("/fobs", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Fob.model_validate(item) for item in data]
        return []

    async def get(self, fob_id: str, site_id: str | None = None) -> Fob:
        path = self._client.build_api_path(f"/fobs/{fob_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Fob.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return Fob.model_validate(data[0])
        raise ValueError(f"Fob {fob_id} not found")

    async def update(
        self,
        fob_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> Fob:
        path = self._client.build_api_path(f"/fobs/{fob_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Fob.model_validate(data)
        raise ValueError(f"Failed to update fob {fob_id}")
