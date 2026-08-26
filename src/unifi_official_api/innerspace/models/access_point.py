"""Access point models for UniFi InnerSpace."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class InnerSpaceMountType(StrEnum):
    """InnerSpace access point mount type."""

    CEILING = "ceiling"
    WALL = "wall"
    RACK = "rack"
    FLOOR = "floor"


class InnerSpaceAccessPoint(BaseModel):
    """InnerSpace placed access point."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    model: str
    mac: str | None = None
    serial: str | None = None
    floor_plan_id: str = Field(alias="floor_plan_id")
    x: float
    y: float
    height: float = 2.4
    azimuth: float = 0.0
    mount: str | InnerSpaceMountType | None = None
    status: str = "online"
