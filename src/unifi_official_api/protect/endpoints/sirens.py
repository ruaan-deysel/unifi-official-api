"""Sirens endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.siren import Siren

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class SirensEndpoint:
    """Endpoint for managing UniFi Protect sirens."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[Siren]:
        path = self._client.build_api_path("/sirens", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Siren.model_validate(item) for item in data]
        return []

    async def get(self, siren_id: str, site_id: str | None = None) -> Siren:
        path = self._client.build_api_path(f"/sirens/{siren_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Siren.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return Siren.model_validate(data[0])
        raise ValueError(f"Siren {siren_id} not found")

    async def update(
        self,
        siren_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> Siren:
        path = self._client.build_api_path(f"/sirens/{siren_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Siren.model_validate(data)
        raise ValueError(f"Failed to update siren {siren_id}")

    async def play(
        self,
        siren_id: str,
        duration_seconds: int | None = None,
        volume: int | None = None,
        site_id: str | None = None,
    ) -> None:
        path = self._client.build_api_path(f"/sirens/{siren_id}/play", site_id)
        payload: dict[str, Any] = {}
        if duration_seconds is not None:
            payload["durationSeconds"] = duration_seconds
        if volume is not None:
            payload["volume"] = volume
        await self._client._post(path, json_data=payload)

    async def stop(self, siren_id: str, site_id: str | None = None) -> None:
        path = self._client.build_api_path(f"/sirens/{siren_id}/stop", site_id)
        await self._client._post(path)

    async def test_sound(self, siren_id: str, site_id: str | None = None) -> None:
        path = self._client.build_api_path(f"/sirens/{siren_id}/test-sound", site_id)
        await self._client._post(path)
