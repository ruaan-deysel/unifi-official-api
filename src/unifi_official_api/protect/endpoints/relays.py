"""Relays endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.relay import Relay

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class RelaysEndpoint:
    """Endpoint for managing UniFi Protect relays."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[Relay]:
        path = self._client.build_api_path("/relays", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Relay.model_validate(item) for item in data]
        return []

    async def get(self, relay_id: str, site_id: str | None = None) -> Relay:
        path = self._client.build_api_path(f"/relays/{relay_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Relay.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return Relay.model_validate(data[0])
        raise ValueError(f"Relay {relay_id} not found")

    async def update(
        self,
        relay_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> Relay:
        path = self._client.build_api_path(f"/relays/{relay_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Relay.model_validate(data)
        raise ValueError(f"Failed to update relay {relay_id}")

    async def activate_output(
        self,
        relay_id: str,
        output_id: int | str,
        duration_ms: int | None = None,
        site_id: str | None = None,
    ) -> None:
        path = self._client.build_api_path(
            f"/relays/{relay_id}/outputs/{output_id}/activate", site_id
        )
        payload: dict[str, Any] = {}
        if duration_ms is not None:
            payload["durationMs"] = duration_ms
        await self._client._post(path, json_data=payload)
