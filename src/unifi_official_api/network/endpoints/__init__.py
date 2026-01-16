"""Endpoint modules for UniFi Network API."""

from __future__ import annotations

from .clients import ClientsEndpoint
from .devices import DevicesEndpoint
from .firewall import FirewallEndpoint
from .networks import NetworksEndpoint
from .sites import SitesEndpoint
from .wifi import WifiEndpoint

__all__ = [
    "ClientsEndpoint",
    "DevicesEndpoint",
    "FirewallEndpoint",
    "NetworksEndpoint",
    "SitesEndpoint",
    "WifiEndpoint",
]
