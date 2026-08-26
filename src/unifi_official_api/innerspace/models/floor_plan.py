"""Floor plan models for UniFi InnerSpace."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class FloorPlan(BaseModel):
    """InnerSpace floor plan."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str
    floor_number: float | None = Field(default=None, alias="floor_number")
    image_url: str | None = Field(default=None, alias="image_url")
    ppm: float | None = None
    width: float | None = None
    height: float | None = None
    origin_x: float | None = Field(default=None, alias="origin_x")
    origin_y: float | None = Field(default=None, alias="origin_y")
    site_id: str | None = Field(default=None, alias="site_id")
