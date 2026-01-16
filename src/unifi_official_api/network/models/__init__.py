"""Pydantic models for UniFi Network API."""

from __future__ import annotations

from .client import Client, ClientType
from .device import Device, DevicePort, DeviceState, DeviceType
from .firewall import FirewallRule, FirewallZone
from .network import Network, NetworkPurpose, NetworkType
from .site import Site, SiteHealth
from .wifi import WifiNetwork, WifiSecurity

__all__ = [
    "Client",
    "ClientType",
    "Device",
    "DevicePort",
    "DeviceState",
    "DeviceType",
    "FirewallRule",
    "FirewallZone",
    "Network",
    "NetworkPurpose",
    "NetworkType",
    "Site",
    "SiteHealth",
    "WifiNetwork",
    "WifiSecurity",
]
