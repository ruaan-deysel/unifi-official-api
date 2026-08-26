"""Service plans endpoint for UniFi Carrier Fabric API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.service_plan import ServicePlan, ServicePlanListResponse

if TYPE_CHECKING:
    from ..client import UniFiCarrierFabricClient


class ServicePlansEndpoint:
    """Endpoint for managing Carrier Fabric bandwidth/QoS service plans."""

    def __init__(self, client: UniFiCarrierFabricClient) -> None:
        self._client = client

    async def get_all(
        self,
        *,
        status: str | None = None,
    ) -> list[ServicePlan]:
        params: dict[str, Any] = {}
        if status:
            params["status"] = status
        response = await self._client._get(
            "/v1/carrier/service-plans", params=params if params else None
        )
        if isinstance(response, dict):
            list_resp = ServicePlanListResponse.model_validate(response)
            return list_resp.data
        return []

    async def get(self, plan_id: str) -> ServicePlan:
        response = await self._client._get(f"/v1/carrier/service-plans/{plan_id}")
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "id" in data:
                return ServicePlan.model_validate(data)
        raise ValueError(f"Service plan {plan_id} not found")
