"""Relay models for UniFi Protect."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RelayOutput(BaseModel):
    """Relay output port."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: int
    name: str | None = None
    state: str = "OPEN"
    duration_ms: int | None = Field(default=None, alias="durationMs")


class Relay(BaseModel):
    """UniFi Protect Relay device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="relay", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "relay"
    guid: str | None = None
    mac: str = ""
    outputs: list[RelayOutput] = Field(default_factory=list)
    inputs: list[dict[str, Any]] = Field(default_factory=list)
