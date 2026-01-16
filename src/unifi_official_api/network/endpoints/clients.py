"""Clients endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Client

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class ClientsEndpoint:
    """Endpoint for managing network clients."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the clients endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def list(
        self,
        host_id: str,
        site_id: str | None = None,
    ) -> list[Client]:
        """List all connected clients.

        Args:
            host_id: The host ID.
            site_id: Optional site ID to filter by.

        Returns:
            List of clients.
        """
        params: dict[str, Any] = {}
        if site_id:
            params["siteId"] = site_id

        path = f"/ea/hosts/{host_id}/clients"
        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Client.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, client_id: str) -> Client:
        """Get a specific client.

        Args:
            host_id: The host ID.
            client_id: The client ID or MAC address.

        Returns:
            The client.
        """
        path = f"/ea/hosts/{host_id}/clients/{client_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Client.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Client.model_validate(data[0])
        raise ValueError(f"Client {client_id} not found")

    async def block(self, host_id: str, site_id: str, mac: str) -> bool:
        """Block a client.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            mac: The client MAC address.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/clients/{mac}/block"
        await self._client._post(path)
        return True

    async def unblock(self, host_id: str, site_id: str, mac: str) -> bool:
        """Unblock a client.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            mac: The client MAC address.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/clients/{mac}/unblock"
        await self._client._post(path)
        return True

    async def reconnect(self, host_id: str, site_id: str, mac: str) -> bool:
        """Force a client to reconnect.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            mac: The client MAC address.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/clients/{mac}/reconnect"
        await self._client._post(path)
        return True
