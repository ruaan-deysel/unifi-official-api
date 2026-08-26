"""User models for UniFi Protect."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ProtectUser(BaseModel):
    """UniFi Protect local user."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str = ""
    first_name: str | None = Field(default=None, alias="firstName")
    last_name: str | None = Field(default=None, alias="lastName")
    email: str | None = None
    ucore_user_id: str | None = Field(default=None, alias="ucoreUserId")
    model_key: str = Field(default="user", alias="modelKey")


class ULPUser(BaseModel):
    """UniFi Identity (ULP) user."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    full_name: str = Field(alias="fullName")
    email: str = ""
    status: str = "ACTIVE"
    model_key: str = Field(default="ulpUser", alias="modelKey")
