"""Firewall models for UniFi Network API."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class FirewallZone(BaseModel):
    """Model representing a firewall zone."""

    id: str
    name: str
    site_id: str | None = Field(default=None, alias="siteId")
    network_ids: list[str] = Field(default_factory=list, alias="networkIds")

    model_config = {"populate_by_name": True, "extra": "allow"}


class FirewallAction(StrEnum):
    """Firewall rule actions."""

    ACCEPT = "accept"
    DROP = "drop"
    REJECT = "reject"


class FirewallProtocol(StrEnum):
    """Firewall protocols."""

    ALL = "all"
    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    TCP_UDP = "tcp_udp"


class FirewallRule(BaseModel):
    """Model representing a firewall rule."""

    id: str
    name: str
    site_id: str | None = Field(default=None, alias="siteId")
    enabled: bool = True
    action: FirewallAction = FirewallAction.DROP
    protocol: FirewallProtocol = FirewallProtocol.ALL
    source_zone_id: str | None = Field(default=None, alias="sourceZoneId")
    destination_zone_id: str | None = Field(default=None, alias="destinationZoneId")
    source_address: str | None = Field(default=None, alias="sourceAddress")
    destination_address: str | None = Field(default=None, alias="destinationAddress")
    source_port: str | None = Field(default=None, alias="sourcePort")
    destination_port: str | None = Field(default=None, alias="destinationPort")
    index: int | None = None
    logging: bool = False

    model_config = {"populate_by_name": True, "extra": "allow"}
