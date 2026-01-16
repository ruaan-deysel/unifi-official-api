"""Device models for UniFi Network API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeviceType(str, Enum):
    """Types of UniFi network devices."""

    UGW = "ugw"  # UniFi Gateway
    USW = "usw"  # UniFi Switch
    UAP = "uap"  # UniFi Access Point
    UXG = "uxg"  # UniFi Next-Gen Gateway
    UDM = "udm"  # UniFi Dream Machine
    UDMPRO = "udm-pro"  # UniFi Dream Machine Pro
    UCK = "uck"  # UniFi Cloud Key


class DeviceState(str, Enum):
    """Device connection states."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ADOPTING = "adopting"
    PROVISIONING = "provisioning"
    UPGRADING = "upgrading"
    UNKNOWN = "unknown"


class DevicePort(BaseModel):
    """Model representing a device port."""

    port_idx: int = Field(alias="portIdx")
    name: str | None = None
    enabled: bool = True
    speed: int | None = None
    full_duplex: bool | None = Field(default=None, alias="fullDuplex")
    is_uplink: bool = Field(default=False, alias="isUplink")
    poe_enabled: bool | None = Field(default=None, alias="poeEnabled")
    poe_power: float | None = Field(default=None, alias="poePower")

    model_config = {"populate_by_name": True, "extra": "allow"}


class Device(BaseModel):
    """Model representing a UniFi network device."""

    id: str
    mac: str
    name: str | None = None
    model: str | None = None
    type: DeviceType | None = None
    state: DeviceState = DeviceState.UNKNOWN
    ip: str | None = None
    firmware_version: str | None = Field(default=None, alias="firmwareVersion")
    uptime: int | None = None
    last_seen: datetime | None = Field(default=None, alias="lastSeen")
    adopted: bool = False
    site_id: str | None = Field(default=None, alias="siteId")
    ports: list[DevicePort] = Field(default_factory=list)
    cpu_utilization: float | None = Field(default=None, alias="cpuUtilization")
    memory_utilization: float | None = Field(default=None, alias="memoryUtilization")
    tx_bytes: int | None = Field(default=None, alias="txBytes")
    rx_bytes: int | None = Field(default=None, alias="rxBytes")
    extra: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True, "extra": "allow"}
