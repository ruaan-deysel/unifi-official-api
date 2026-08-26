"""Switches endpoint for UniFi InnerSpace API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.switch import InnerSpaceSwitch

if TYPE_CHECKING:
    from ..client import UniFiInnerSpaceClient


class SwitchesEndpoint:
    """Endpoint for retrieving UniFi InnerSpace placed switches."""

    def __init__(self, client: UniFiInnerSpaceClient) -> None:
        """
        Initialize the switches endpoint.

        Args:
            client: The UniFi InnerSpace client.
        """
        self._client = client

    async def get_all(self, site_id: str | None = None) -> list[InnerSpaceSwitch]:
        """
        List placed switches.

        Args:
            site_id: Optional site ID filter.

        Returns:
            List of placed switches.
        """
        path = self._client.build_api_path("/switches")
        params: dict[str, Any] = {}
        if site_id:
            params["siteId"] = site_id
        response = await self._client._get(path, params=params if params else None)
        if response is None:
            return []
        if isinstance(response, dict):
            sws = response.get("switches", response.get("data", []))
            if isinstance(sws, list):
                return [InnerSpaceSwitch.model_validate(item) for item in sws]
        return []
