"""Endpoint modules for UniFi Network API."""

from __future__ import annotations

from .devices import DevicesEndpoint
from .clients import ClientsEndpoint
from .networks import NetworksEndpoint
from .wifi import WifiEndpoint
from .sites import SitesEndpoint
from .firewall import FirewallEndpoint

__all__ = [
    "ClientsEndpoint",
    "DevicesEndpoint",
    "FirewallEndpoint",
    "NetworksEndpoint",
    "SitesEndpoint",
    "WifiEndpoint",
]
