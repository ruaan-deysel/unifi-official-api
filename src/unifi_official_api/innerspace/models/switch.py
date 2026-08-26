"""Switch models for UniFi InnerSpace."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class InnerSpaceSwitch(BaseModel):
    """InnerSpace placed switch."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    model: str
    type: str = "switch"
    mac: str | None = None
    serial: str | None = None
    floor_plan_id: str = Field(alias="floor_plan_id")
    x: float
    y: float
    status: str = "online"
