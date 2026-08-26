"""Alarm Manager endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class AlarmManagerEndpoint:
    """Endpoint for UniFi Protect Alarm Manager integration."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """
        Initialize the Alarm Manager endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def send_webhook(
        self,
        webhook_id: str,
        payload: dict[str, Any] | None = None,
        site_id: str | None = None,
    ) -> None:
        """
        Send a webhook trigger to the alarm manager.

        Args:
            webhook_id: Webhook identifier.
            payload: Optional payload to send.
            site_id: Optional site ID.
        """
        path = self._client.build_api_path(f"/alarm-manager/webhook/{webhook_id}", site_id)
        await self._client._post(path, json_data=payload or {})
