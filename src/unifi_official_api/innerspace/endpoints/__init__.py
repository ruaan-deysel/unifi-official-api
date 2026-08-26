"""Endpoint modules for UniFi InnerSpace API."""

from __future__ import annotations

from .access_points import AccessPointsEndpoint
from .assets import AssetsEndpoint
from .floor_plans import FloorPlansEndpoint
from .inventory import InventoryEndpoint
from .project import ProjectEndpoint
from .switches import SwitchesEndpoint

__all__ = [
    "AccessPointsEndpoint",
    "AssetsEndpoint",
    "FloorPlansEndpoint",
    "InventoryEndpoint",
    "ProjectEndpoint",
    "SwitchesEndpoint",
]
