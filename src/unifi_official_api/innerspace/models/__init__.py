"""Pydantic models for UniFi InnerSpace API."""

from __future__ import annotations

from .access_point import InnerSpaceAccessPoint, InnerSpaceMountType
from .floor_plan import FloorPlan
from .inventory import InventoryDevice
from .project import ProjectData, ProjectMeta
from .switch import InnerSpaceSwitch

__all__ = [
    "FloorPlan",
    "InnerSpaceAccessPoint",
    "InnerSpaceMountType",
    "InnerSpaceSwitch",
    "InventoryDevice",
    "ProjectData",
    "ProjectMeta",
]
