"""Point of Sale (POS) endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.pos import POSTransactionRequest

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class POSEndpoint:
    """Endpoint for ingesting POS transactions on UniFi Protect cameras."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """
        Initialize the POS endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def ingest_transaction(
        self,
        camera_id: str,
        transaction: POSTransactionRequest | dict[str, Any],
        site_id: str | None = None,
    ) -> None:
        """
        Ingest a POS transaction onto camera footage.

        Args:
            camera_id: Target camera ID.
            transaction: POS transaction model or dictionary.
            site_id: Optional site ID.
        """
        payload = (
            transaction.model_dump(by_alias=True, exclude_none=True)
            if isinstance(transaction, POSTransactionRequest)
            else transaction
        )
        path = self._client.build_api_path(f"/pos/cameras/{camera_id}/transactions", site_id)
        await self._client._post(path, json_data=payload)
