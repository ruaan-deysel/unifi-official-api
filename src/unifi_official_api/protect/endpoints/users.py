"""Users endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.user import ProtectUser, ULPUser

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class UsersEndpoint:
    """Endpoint for managing UniFi Protect local and identity users."""

    def __init__(self, client: UniFiProtectClient) -> None:
        self._client = client

    async def get_users(self, site_id: str | None = None) -> list[ProtectUser]:
        path = self._client.build_api_path("/users", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [ProtectUser.model_validate(item) for item in data]
        return []

    async def get_user(self, user_id: str, site_id: str | None = None) -> ProtectUser:
        path = self._client.build_api_path(f"/users/{user_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return ProtectUser.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return ProtectUser.model_validate(data[0])
        raise ValueError(f"User {user_id} not found")

    async def get_ulp_users(self, site_id: str | None = None) -> list[ULPUser]:
        path = self._client.build_api_path("/ulp-users", site_id)
        response = await self._client._get(path)
        if response is None:
            return []
        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [ULPUser.model_validate(item) for item in data]
        return []

    async def get_ulp_user(self, ulp_user_id: str, site_id: str | None = None) -> ULPUser:
        path = self._client.build_api_path(f"/ulp-users/{ulp_user_id}", site_id)
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return ULPUser.model_validate(data)
            if (
                isinstance(data, list)
                and len(data) > 0
                and isinstance(data[0], dict)
                and "id" in data[0]
            ):
                return ULPUser.model_validate(data[0])
        raise ValueError(f"ULP User {ulp_user_id} not found")
