"""Client models for UniFi Network API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ClientType(str, Enum):
    """Types of network clients."""

    WIRED = "wired"
    WIRELESS = "wireless"


class Client(BaseModel):
    """Model representing a connected network client."""

    id: str
    mac: str
    name: str | None = None
    hostname: str | None = None
    ip: str | None = None
    type: ClientType | None = None
    network_id: str | None = Field(default=None, alias="networkId")
    site_id: str | None = Field(default=None, alias="siteId")
    connected: bool = True
    authorized: bool = True
    blocked: bool = False
    first_seen: datetime | None = Field(default=None, alias="firstSeen")
    last_seen: datetime | None = Field(default=None, alias="lastSeen")
    uptime: int | None = None
    tx_bytes: int | None = Field(default=None, alias="txBytes")
    rx_bytes: int | None = Field(default=None, alias="rxBytes")
    tx_rate: int | None = Field(default=None, alias="txRate")
    rx_rate: int | None = Field(default=None, alias="rxRate")
    signal: int | None = None
    noise: int | None = None
    channel: int | None = None
    radio: str | None = None
    essid: str | None = None
    bssid: str | None = None
    ap_mac: str | None = Field(default=None, alias="apMac")
    sw_mac: str | None = Field(default=None, alias="swMac")
    sw_port: int | None = Field(default=None, alias="swPort")
    vlan: int | None = None
    os_name: str | None = Field(default=None, alias="osName")
    device_name: str | None = Field(default=None, alias="deviceName")

    model_config = {"populate_by_name": True, "extra": "allow"}

    @property
    def display_name(self) -> str:
        """Get the display name for the client."""
        return self.name or self.hostname or self.mac
