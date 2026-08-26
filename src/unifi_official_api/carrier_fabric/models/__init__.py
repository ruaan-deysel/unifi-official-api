"""Pydantic models for UniFi Carrier Fabric API."""

from __future__ import annotations

from .service_plan import ServicePlan, ServicePlanListResponse
from .subscriber import (
    HostLinkResponse,
    Meta,
    Subscriber,
    SubscriberCreate,
    SubscriberListResponse,
    SubscriberPatch,
)

__all__ = [
    "HostLinkResponse",
    "Meta",
    "ServicePlan",
    "ServicePlanListResponse",
    "Subscriber",
    "SubscriberCreate",
    "SubscriberListResponse",
    "SubscriberPatch",
]
