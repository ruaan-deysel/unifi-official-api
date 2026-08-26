"""Speakers endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.speaker import Speaker

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class SpeakersEndpoint:
    """Endpoint for managing UniFi Protect speakers."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[Speaker]:
        path = self._client.build_api_path("/speakers", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Speaker.model_validate(item) for item in data]
        return []

    async def get(self, speaker_id: str, site_id: str | None = None) -> Speaker:
        path = self._client.build_api_path(f"/speakers/{speaker_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Speaker.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return Speaker.model_validate(data[0])
        raise ValueError(f"Speaker {speaker_id} not found")

    async def update(
        self,
        speaker_id: str,
        site_id: str | None = None,
        **kwargs: Any,
    ) -> Speaker:
        path = self._client.build_api_path(f"/speakers/{speaker_id}", site_id)
        response = await self._client._patch(path, json_data=kwargs)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Speaker.model_validate(data)
        raise ValueError(f"Failed to update speaker {speaker_id}")

    async def test_sound(self, speaker_id: str, site_id: str | None = None) -> None:
        path = self._client.build_api_path(f"/speakers/{speaker_id}/test-sound", site_id)
        await self._client._post(path)
