"""Pydantic models for UniFi Network API."""

from __future__ import annotations

from .acl import (
    ACLAction,
    ACLDestinationFilter,
    ACLDeviceFilter,
    ACLMetadata,
    ACLRule,
    ACLRuleType,
    ACLSourceFilter,
    MetadataOrigin,
)
from .client import Client, ClientType
from .device import Device, DevicePort, DeviceState, DeviceType
from .firewall import FirewallRule, FirewallZone
from .network import Network, NetworkPurpose, NetworkType
from .resources import (
    DeviceTag,
    RADIUSProfile,
    VPNServer,
    VPNServerType,
    VPNTunnel,
    VPNTunnelStatus,
    WANInterface,
    WANStatus,
)
from .site import Site, SiteHealth
from .traffic import (
    Country,
    DPIApplication,
    DPICategory,
    TrafficMatchingList,
    TrafficMatchingType,
)
from .voucher import Voucher, VoucherCreateRequest
from .wifi import WifiNetwork, WifiSecurity

__all__ = [
    # ACL
    "ACLAction",
    "ACLDestinationFilter",
    "ACLDeviceFilter",
    "ACLMetadata",
    "ACLRule",
    "ACLRuleType",
    "ACLSourceFilter",
    "MetadataOrigin",
    # Client
    "Client",
    "ClientType",
    # Device
    "Device",
    "DevicePort",
    "DeviceState",
    "DeviceType",
    # Firewall
    "FirewallRule",
    "FirewallZone",
    # Network
    "Network",
    "NetworkPurpose",
    "NetworkType",
    # Resources
    "DeviceTag",
    "RADIUSProfile",
    "VPNServer",
    "VPNServerType",
    "VPNTunnel",
    "VPNTunnelStatus",
    "WANInterface",
    "WANStatus",
    # Site
    "Site",
    "SiteHealth",
    # Traffic
    "Country",
    "DPIApplication",
    "DPICategory",
    "TrafficMatchingList",
    "TrafficMatchingType",
    # Voucher
    "Voucher",
    "VoucherCreateRequest",
    # WiFi
    "WifiNetwork",
    "WifiSecurity",
]
