"""Chimes endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Chime

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class ChimesEndpoint:
    """Endpoint for managing UniFi Protect chimes."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """Initialize the chimes endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def get_all(self, host_id: str, site_id: str) -> list[Chime]:
        """List all chimes.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            List of chimes.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/chimes"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Chime.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, chime_id: str) -> Chime:
        """Get a specific chime.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            chime_id: The chime ID.

        Returns:
            The chime.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/chimes/{chime_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Chime.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Chime.model_validate(data[0])
        raise ValueError(f"Chime {chime_id} not found")

    async def update(
        self,
        host_id: str,
        site_id: str,
        chime_id: str,
        **kwargs: Any,
    ) -> Chime:
        """Update chime settings.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            chime_id: The chime ID.
            **kwargs: Settings to update.

        Returns:
            The updated chime.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/chimes/{chime_id}"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return Chime.model_validate(result)
        raise ValueError("Failed to update chime")

    async def set_volume(
        self,
        host_id: str,
        site_id: str,
        chime_id: str,
        volume: int,
    ) -> Chime:
        """Set chime volume.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            chime_id: The chime ID.
            volume: Volume level (0-100).

        Returns:
            The updated chime.
        """
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")
        return await self.update(host_id, site_id, chime_id, volume=volume)

    async def play(self, host_id: str, site_id: str, chime_id: str) -> bool:
        """Play the chime sound.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            chime_id: The chime ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/chimes/{chime_id}/play"
        await self._client._post(path)
        return True
