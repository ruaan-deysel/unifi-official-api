"""Project models for UniFi InnerSpace."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProjectMeta(BaseModel):
    """InnerSpace project metadata."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    title: str
    created_at: str | None = Field(default=None, alias="createdAt")
    updated_at: str | None = Field(default=None, alias="updatedAt")


class ProjectData(BaseModel):
    """InnerSpace full project data."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    project: ProjectMeta | None = None
    shapes: list[dict[str, Any]] = Field(default_factory=list)
    plans: list[dict[str, Any]] = Field(default_factory=list)
    products: list[dict[str, Any]] = Field(default_factory=list)
    wall_types: list[dict[str, Any]] = Field(default_factory=list, alias="wallTypes")
    attenuation_object_types: list[dict[str, Any]] = Field(
        default_factory=list, alias="attenuationObjectTypes"
    )
