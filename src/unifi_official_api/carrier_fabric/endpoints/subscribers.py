"""Subscribers endpoint for UniFi Carrier Fabric API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.subscriber import (
    HostLinkResponse,
    Subscriber,
    SubscriberCreate,
    SubscriberListResponse,
    SubscriberPatch,
)

if TYPE_CHECKING:
    from ..client import UniFiCarrierFabricClient


class SubscribersEndpoint:
    """Endpoint for managing ISP subscribers in UniFi Carrier Fabric."""

    def __init__(self, client: UniFiCarrierFabricClient) -> None:
        self._client = client

    async def get_all(
        self,
        *,
        limit: int = 50,
        cursor: str | None = None,
        search: str | None = None,
        state: str | None = None,
    ) -> SubscriberListResponse:
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if search:
            params["search"] = search
        if state:
            params["state"] = state
        response = await self._client._get("/v1/carrier/subscribers", params=params)
        if isinstance(response, dict):
            return SubscriberListResponse.model_validate(response)
        return SubscriberListResponse()

    async def create(
        self,
        subscriber: SubscriberCreate | dict[str, Any],
    ) -> Subscriber:
        payload = (
            subscriber.model_dump(by_alias=True, exclude_none=True)
            if isinstance(subscriber, SubscriberCreate)
            else subscriber
        )
        response = await self._client._post("/v1/carrier/subscribers", json_data=payload)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Subscriber.model_validate(data)
        raise ValueError("Failed to create subscriber")

    async def get(self, subscriber_id: str) -> Subscriber:
        response = await self._client._get(f"/v1/carrier/subscribers/{subscriber_id}")
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Subscriber.model_validate(data)
        raise ValueError(f"Subscriber {subscriber_id} not found")

    async def update(
        self,
        subscriber_id: str,
        patch: SubscriberPatch | dict[str, Any],
    ) -> Subscriber:
        payload = (
            patch.model_dump(by_alias=True, exclude_none=True)
            if isinstance(patch, SubscriberPatch)
            else patch
        )
        response = await self._client._patch(
            f"/v1/carrier/subscribers/{subscriber_id}", json_data=payload
        )
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Subscriber.model_validate(data)
        raise ValueError(f"Failed to update subscriber {subscriber_id}")

    async def attach_host(
        self,
        subscriber_id: str,
        host_id: str,
    ) -> HostLinkResponse:
        response = await self._client._put(
            f"/v1/carrier/subscribers/{subscriber_id}/host",
            json_data={"hostId": host_id},
        )
        if isinstance(response, dict):
            return HostLinkResponse.model_validate(response)
        return HostLinkResponse()

    async def detach_host(self, subscriber_id: str) -> HostLinkResponse:
        response = await self._client._delete(f"/v1/carrier/subscribers/{subscriber_id}/host")
        if isinstance(response, dict):
            return HostLinkResponse.model_validate(response)
        return HostLinkResponse()

    async def assign_plan(self, subscriber_id: str, plan_id: str) -> Subscriber:
        response = await self._client._put(
            f"/v1/carrier/subscribers/{subscriber_id}/plan",
            json_data={"planId": plan_id},
        )
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Subscriber.model_validate(data)
        raise ValueError(f"Failed to assign plan to subscriber {subscriber_id}")

    async def suspend(
        self,
        subscriber_id: str,
        reason: str | None = None,
    ) -> Subscriber:
        payload: dict[str, Any] = {}
        if reason:
            payload["reason"] = reason
        response = await self._client._post(
            f"/v1/carrier/subscribers/{subscriber_id}/suspend", json_data=payload
        )
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Subscriber.model_validate(data)
        raise ValueError(f"Failed to suspend subscriber {subscriber_id}")

    async def resume(self, subscriber_id: str) -> Subscriber:
        response = await self._client._post(f"/v1/carrier/subscribers/{subscriber_id}/resume")
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return Subscriber.model_validate(data)
        raise ValueError(f"Failed to resume subscriber {subscriber_id}")
