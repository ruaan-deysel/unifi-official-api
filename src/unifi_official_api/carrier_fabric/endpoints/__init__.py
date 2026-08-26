"""Endpoint modules for UniFi Carrier Fabric API."""

from __future__ import annotations

from .service_plans import ServicePlansEndpoint
from .subscribers import SubscribersEndpoint

__all__ = [
    "ServicePlansEndpoint",
    "SubscribersEndpoint",
]
