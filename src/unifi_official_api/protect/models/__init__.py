"""Pydantic models for UniFi Protect API."""

from __future__ import annotations

from .alarm import AlarmHub, ArmProfile, ArmProfileSettings
from .bridge import Bridge, LinkStation
from .camera import Camera, CameraState, CameraType, RecordingMode, VideoMode
from .chime import Chime
from .event import Event, EventType
from .files import ApplicationInfo, DeviceFile, FileType, RTSPSStream, TalkbackSession
from .fob import Fob
from .light import Light, LightMode
from .liveview import LiveView
from .nvr import NVR
from .pos import POSLineItem, POSLocation, POSTransactionRequest
from .relay import Relay, RelayOutput
from .sensor import BatteryStatus, Sensor, SensorType
from .siren import Siren, SirenLedSettings, SirenStatus
from .speaker import Speaker, SpeakerFeatureFlags, SpeakerState
from .user import ProtectUser, ULPUser
from .viewer import Viewer, ViewerState

__all__ = [
    # Alarm / Arm Profiles
    "AlarmHub",
    "ArmProfile",
    "ArmProfileSettings",
    # Application/Files
    "ApplicationInfo",
    "DeviceFile",
    "FileType",
    "RTSPSStream",
    "TalkbackSession",
    # Bridge / LinkStation
    "Bridge",
    "LinkStation",
    # Camera
    "Camera",
    "CameraState",
    "CameraType",
    "RecordingMode",
    "VideoMode",
    # Chime
    "Chime",
    # Event
    "Event",
    "EventType",
    # Fob
    "Fob",
    # Light
    "Light",
    "LightMode",
    # LiveView
    "LiveView",
    # NVR
    "NVR",
    # POS
    "POSLineItem",
    "POSLocation",
    "POSTransactionRequest",
    # Relay
    "Relay",
    "RelayOutput",
    # Sensor
    "BatteryStatus",
    "Sensor",
    "SensorType",
    # Siren
    "Siren",
    "SirenLedSettings",
    "SirenStatus",
    # Speaker
    "Speaker",
    "SpeakerFeatureFlags",
    "SpeakerState",
    # Users
    "ProtectUser",
    "ULPUser",
    # Viewer
    "Viewer",
    "ViewerState",
]
