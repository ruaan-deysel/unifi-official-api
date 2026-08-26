"""Fob models for UniFi Protect."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class Fob(BaseModel):
    """UniFi Protect Key Fob device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="fob", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "fob"
    guid: str | None = None
    mac: str = ""
