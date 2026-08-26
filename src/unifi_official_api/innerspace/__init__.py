"""UniFi InnerSpace API module."""

from __future__ import annotations

from .client import UniFiInnerSpaceClient
from .models import (
    FloorPlan,
    InnerSpaceAccessPoint,
    InnerSpaceMountType,
    InnerSpaceSwitch,
    InventoryDevice,
    ProjectData,
    ProjectMeta,
)

__all__ = [
    "FloorPlan",
    "InnerSpaceAccessPoint",
    "InnerSpaceMountType",
    "InnerSpaceSwitch",
    "InventoryDevice",
    "ProjectData",
    "ProjectMeta",
    "UniFiInnerSpaceClient",
]
