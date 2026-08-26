"""Arm Profiles endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.alarm import ArmProfile, ArmProfileSettings

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class ArmProfilesEndpoint:
    """Endpoint for managing UniFi Protect arm profiles."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[ArmProfile]:
        path = self._client.build_api_path("/arm-profiles", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [ArmProfile.model_validate(item) for item in data]
        return []

    async def create(
        self,
        profile_data: dict[str, Any],
        site_id: str | None = None,
    ) -> ArmProfile:
        path = self._client.build_api_path("/arm-profiles", site_id)
        response = await self._client._post(path, json_data=profile_data)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return ArmProfile.model_validate(data)
        raise ValueError("Failed to create arm profile")

    async def update_settings(
        self,
        settings: dict[str, Any],
        site_id: str | None = None,
    ) -> ArmProfileSettings:
        path = self._client.build_api_path("/arm-profiles/settings", site_id)
        response = await self._client._patch(path, json_data=settings)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and ("activeProfileId" in data or "isArmed" in data):
                return ArmProfileSettings.model_validate(data)
        raise ValueError("Failed to update arm profile settings")

    async def update(
        self,
        profile_id: str,
        data: dict[str, Any],
        site_id: str | None = None,
    ) -> ArmProfile:
        path = self._client.build_api_path(f"/arm-profiles/{profile_id}", site_id)
        response = await self._client._patch(path, json_data=data)
        if isinstance(response, dict):
            resp_data = response.get("data", response)
            if isinstance(resp_data, dict) and "id" in resp_data:
                return ArmProfile.model_validate(resp_data)
        raise ValueError(f"Failed to update arm profile {profile_id}")

    async def delete(self, profile_id: str, site_id: str | None = None) -> None:
        path = self._client.build_api_path(f"/arm-profiles/{profile_id}", site_id)
        await self._client._delete(path)

    async def enable(self, site_id: str | None = None) -> None:
        path = self._client.build_api_path("/arm-profiles/enable", site_id)
        await self._client._post(path)

    async def disable(self, site_id: str | None = None) -> None:
        path = self._client.build_api_path("/arm-profiles/disable", site_id)
        await self._client._post(path)
