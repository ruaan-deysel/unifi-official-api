"""Speaker models for UniFi Protect."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SpeakerState(BaseModel):
    """Speaker state information."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    status: str = "idle"
    mode: str = "default"


class SpeakerFeatureFlags(BaseModel):
    """Speaker hardware feature flags."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    has_mic: bool = Field(default=False, alias="hasMic")


class Speaker(BaseModel):
    """UniFi Protect Speaker device."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str
    name: str | None = None
    model_key: str = Field(default="speaker", alias="modelKey")
    state: str = "CONNECTED"
    type: str = "speaker"
    guid: str | None = None
    mac: str = ""
    volume: int = 100
    mic_volume: int = Field(default=100, alias="micVolume")
    is_mic_enabled: bool = Field(default=False, alias="isMicEnabled")
    speaker_state: SpeakerState | None = Field(default=None, alias="speakerState")
    feature_flags: SpeakerFeatureFlags | None = Field(default=None, alias="featureFlags")
