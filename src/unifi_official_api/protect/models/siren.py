"""Siren models for UniFi Protect."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SirenLedSettings(BaseModel):
    """Siren LED settings."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    is_enabled: bool = Field(default=True, alias="isEnabled")


class SirenStatus(BaseModel):
    """Siren operating status."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    is_active: bool = Field(default=False, alias="isActive")
    activated_at: int | None = Field(default=None, alias="activatedAt")
    duration: int | None = None


class Siren(BaseModel):
    """UniFi Protect Siren device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="siren", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "siren"
    guid: str | None = None
    mac: str = ""
    volume: int = 100
    led_settings: SirenLedSettings | None = Field(default=None, alias="ledSettings")
    status: SirenStatus | None = None
