"""Endpoint modules for UniFi Protect API."""

from __future__ import annotations

from .cameras import CamerasEndpoint
from .sensors import SensorsEndpoint
from .lights import LightsEndpoint
from .chimes import ChimesEndpoint
from .nvr import NVREndpoint
from .liveviews import LiveViewsEndpoint
from .events import EventsEndpoint

__all__ = [
    "CamerasEndpoint",
    "ChimesEndpoint",
    "EventsEndpoint",
    "LightsEndpoint",
    "LiveViewsEndpoint",
    "NVREndpoint",
    "SensorsEndpoint",
]
