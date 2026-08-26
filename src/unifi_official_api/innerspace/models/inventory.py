"""Inventory device models for UniFi InnerSpace."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class InventoryDevice(BaseModel):
    """InnerSpace unplaced hardware device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    model: str
    mac: str | None = None
    serial: str | None = None
