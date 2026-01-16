"""Pydantic models for UniFi Network API."""

from __future__ import annotations

from .device import Device, DevicePort, DeviceState, DeviceType
from .client import Client, ClientType
from .network import Network, NetworkPurpose, NetworkType
from .wifi import WifiNetwork, WifiSecurity
from .site import Site, SiteHealth
from .firewall import FirewallRule, FirewallZone

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
