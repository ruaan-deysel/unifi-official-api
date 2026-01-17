"""Sites endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Site

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class SitesEndpoint:
    """Endpoint for managing UniFi sites."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the sites endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def get_all(self, host_id: str) -> list[Site]:
        """List all sites.

        Args:
            host_id: The host ID.

        Returns:
            List of sites.
        """
        path = f"/ea/hosts/{host_id}/sites"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Site.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str) -> Site:
        """Get a specific site.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            The site.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Site.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Site.model_validate(data[0])
        raise ValueError(f"Site {site_id} not found")
