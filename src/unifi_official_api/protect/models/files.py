"""File/Asset models for UniFi Protect API."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FileType(str, Enum):
    """Device asset file type."""

    ANIMATIONS = "animations"


class DeviceFile(BaseModel):
    """Device asset file model."""

    name: str = Field(..., description="Unique file ID")
    type: FileType = Field(..., description="File type")
    original_name: str = Field(..., alias="originalName", description="Original filename")
    path: str = Field(..., description="Filesystem path")

    model_config = {"populate_by_name": True}


class ApplicationInfo(BaseModel):
    """Protect application information."""

    application_version: str = Field(..., alias="applicationVersion")

    model_config = {"populate_by_name": True}


class TalkbackSession(BaseModel):
    """Camera talkback session model."""

    url: str = Field(..., description="Talkback stream URL")
    codec: str = Field(..., description="Audio codec (e.g., opus)")
    sampling_rate: int = Field(..., alias="samplingRate", description="Audio sampling rate")
    bits_per_sample: int = Field(..., alias="bitsPerSample", description="Bits per sample")

    model_config = {"populate_by_name": True}


class RTSPSStream(BaseModel):
    """RTSPS stream configuration."""

    url: str | None = Field(None, description="RTSPS stream URL")
    channel: int | None = Field(None, description="Stream channel")

    model_config = {"populate_by_name": True}
