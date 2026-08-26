"""Subscriber models for UniFi Carrier Fabric."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Meta(BaseModel):
    """Pagination metadata."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    next_cursor: str | None = Field(default=None, alias="nextCursor")
    limit: int | None = None
    has_more: bool | None = Field(default=None, alias="hasMore")


class Subscriber(BaseModel):
    """UniFi Carrier Fabric subscriber."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    org_id: str | None = Field(default=None, alias="orgId")
    subscriber_number: str | None = Field(default=None, alias="subscriberNumber")
    name: str | None = None
    email: str | None = None
    notes: str | None = None
    service_address: str | None = Field(default=None, alias="serviceAddress")
    plan_id: str | None = Field(default=None, alias="planId")
    host_id: str | None = Field(default=None, alias="hostId")
    state: str = "pending_assignment"
    suspended: bool = False
    suspend_reason: str | None = Field(default=None, alias="suspendReason")
    suspended_at: str | None = Field(default=None, alias="suspendedAt")
    metadata: dict[str, Any] | None = None
    activated_at: str | None = Field(default=None, alias="activatedAt")
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class SubscriberCreate(BaseModel):
    """Payload to create a subscriber."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    subscriber_number: str = Field(alias="subscriberNumber")
    name: str | None = None
    email: str | None = None
    notes: str | None = None
    service_address: str | None = Field(default=None, alias="serviceAddress")
    plan_id: str | None = Field(default=None, alias="planId")
    metadata: dict[str, Any] | None = None


class SubscriberPatch(BaseModel):
    """Payload to update a subscriber."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    subscriber_number: str | None = Field(default=None, alias="subscriberNumber")
    name: str | None = None
    email: str | None = None
    notes: str | None = None
    service_address: str | None = Field(default=None, alias="serviceAddress")
    plan_id: str | None = Field(default=None, alias="planId")
    metadata: dict[str, Any] | None = None


class HostLinkResponse(BaseModel):
    """Response after attaching or detaching a host from a subscriber."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    data: Subscriber | None = None
    prev_host_id: str | None = Field(default=None, alias="prevHostId")
    trace_id: str | None = Field(default=None, alias="traceId")


class SubscriberListResponse(BaseModel):
    """Response envelope for listing subscribers."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    data: list[Subscriber] = Field(default_factory=list)
    meta: Meta | None = None
    trace_id: str | None = Field(default=None, alias="traceId")
