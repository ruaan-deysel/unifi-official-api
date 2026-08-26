"""Service plan models for UniFi Carrier Fabric."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ServicePlan(BaseModel):
    """Bandwidth / QoS service plan for Carrier Fabric subscribers."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    org_id: str | None = Field(default=None, alias="orgId")
    name: str
    status: str = "active"
    download_mbps: float | None = Field(default=None, alias="downloadMbps")
    upload_mbps: float | None = Field(default=None, alias="uploadMbps")
    metadata: dict[str, Any] | None = None
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")
    archived_at: str | None = Field(default=None, alias="archivedAt")


class ServicePlanListResponse(BaseModel):
    """Response envelope for listing service plans."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    data: list[ServicePlan] = Field(default_factory=list)
    trace_id: str | None = Field(default=None, alias="traceId")
