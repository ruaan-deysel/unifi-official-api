"""Alarm and Arm Profile models for UniFi Protect."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ArmProfileSettings(BaseModel):
    """Arm profile active settings."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    active_profile_id: str | None = Field(default=None, alias="activeProfileId")
    is_armed: bool = Field(default=False, alias="isArmed")


class ArmProfile(BaseModel):
    """UniFi Protect Arm Profile."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    automations: list[dict[str, Any]] = Field(default_factory=list)
    creator: str | None = None
    schedules: list[dict[str, Any]] = Field(default_factory=list)
    record_everything: bool = Field(default=False, alias="recordEverything")
    activation_delay: int = Field(default=0, alias="activationDelay")
    created_at: int | None = Field(default=None, alias="createdAt")
    updated_at: int | None = Field(default=None, alias="updatedAt")


class AlarmHub(BaseModel):
    """UniFi Protect Alarm Hub device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="alarmHub", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "alarmHub"
    guid: str | None = None
    mac: str = ""
    outputs: list[dict[str, Any]] = Field(default_factory=list)
