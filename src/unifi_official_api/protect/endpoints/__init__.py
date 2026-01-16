"""Endpoint modules for UniFi Protect API."""

from __future__ import annotations

from .cameras import CamerasEndpoint
from .chimes import ChimesEndpoint
from .events import EventsEndpoint
from .lights import LightsEndpoint
from .liveviews import LiveViewsEndpoint
from .nvr import NVREndpoint
from .sensors import SensorsEndpoint

__all__ = [
    "CamerasEndpoint",
    "ChimesEndpoint",
    "EventsEndpoint",
    "LightsEndpoint",
    "LiveViewsEndpoint",
    "NVREndpoint",
    "SensorsEndpoint",
]
