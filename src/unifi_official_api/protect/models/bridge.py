"""Bridge and Link Station models for UniFi Protect."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Bridge(BaseModel):
    """UniFi Protect Bridge device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="bridge", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "bridge"
    guid: str | None = None
    mac: str = ""
    platform: str | None = None
    clients: list[str] = Field(default_factory=list)
    max_clients: int = Field(default=16, alias="maxClients")


class LinkStation(BaseModel):
    """UniFi Protect Link Station device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="linkStation", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "linkStation"
    guid: str | None = None
    mac: str = ""
    is_alarm_hub: bool = Field(default=False, alias="isAlarmHub")
    led_settings: dict[str, Any] | None = Field(default=None, alias="ledSettings")
    alarm_hub: dict[str, Any] | None = Field(default=None, alias="alarmHub")
