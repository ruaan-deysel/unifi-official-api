"""Alarm Hubs endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.alarm import AlarmHub

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class AlarmHubsEndpoint:
    """Endpoint for managing UniFi Protect alarm hubs."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[AlarmHub]:
        path = self._client.build_api_path("/alarm-hubs", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [AlarmHub.model_validate(item) for item in data]
        return []

    async def get(self, hub_id: str, site_id: str | None = None) -> AlarmHub:
        path = self._client.build_api_path(f"/alarm-hubs/{hub_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return AlarmHub.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return AlarmHub.model_validate(data[0])
        raise ValueError(f"Alarm hub {hub_id} not found")

    async def update(
        self,
        hub_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> AlarmHub:
        path = self._client.build_api_path(f"/alarm-hubs/{hub_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return AlarmHub.model_validate(data)
        raise ValueError(f"Failed to update alarm hub {hub_id}")

    async def trigger_output(
        self,
        hub_id: str,
        output_id: int | str,
        site_id: str | None = None,
    ) -> None:
        path = self._client.build_api_path(
            f"/alarm-hubs/{hub_id}/outputs/{output_id}/trigger", site_id
        )
        await self._client._post(path)
