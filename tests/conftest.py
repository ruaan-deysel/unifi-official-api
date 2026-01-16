"""Pytest configuration and fixtures."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth
from unifi_official_api.network import UniFiNetworkClient
from unifi_official_api.protect import UniFiProtectClient


@pytest.fixture
def api_key() -> str:
    """Return a test API key."""
    return "test-api-key-12345"


@pytest.fixture
def auth(api_key: str) -> ApiKeyAuth:
    """Return a test ApiKeyAuth instance."""
    return ApiKeyAuth(api_key=api_key)


@pytest.fixture
def host_id() -> str:
    """Return a test host ID."""
    return "test-host-id"


@pytest.fixture
def site_id() -> str:
    """Return a test site ID."""
    return "test-site-id"


@pytest.fixture
def mock_aioresponse():
    """Provide aioresponses mock context manager."""
    with aioresponses() as m:
        yield m


@pytest.fixture
async def network_client(auth: ApiKeyAuth) -> UniFiNetworkClient:
    """Create a UniFi Network client for testing."""
    client = UniFiNetworkClient(auth=auth)
    yield client
    await client.close()


@pytest.fixture
async def protect_client(auth: ApiKeyAuth) -> UniFiProtectClient:
    """Create a UniFi Protect client for testing."""
    client = UniFiProtectClient(auth=auth)
    yield client
    await client.close()


@pytest.fixture
def sample_device() -> dict[str, Any]:
    """Return sample device data."""
    return {
        "id": "device-123",
        "mac": "00:11:22:33:44:55",
        "name": "Test Switch",
        "model": "USW-24-POE",
        "type": "usw",
        "state": "connected",
        "ip": "192.168.1.10",
        "firmwareVersion": "6.5.28",
        "uptime": 86400,
        "adopted": True,
        "siteId": "site-123",
    }


@pytest.fixture
def sample_client() -> dict[str, Any]:
    """Return sample client data."""
    return {
        "id": "client-123",
        "mac": "AA:BB:CC:DD:EE:FF",
        "name": "Test Device",
        "hostname": "test-device",
        "ip": "192.168.1.100",
        "type": "wireless",
        "connected": True,
        "txBytes": 1000000,
        "rxBytes": 2000000,
    }


@pytest.fixture
def sample_camera() -> dict[str, Any]:
    """Return sample camera data."""
    return {
        "id": "camera-123",
        "mac": "11:22:33:44:55:66",
        "name": "Front Door",
        "type": "UVC G4 Doorbell",
        "model": "UVC G4 Doorbell",
        "state": "CONNECTED",
        "host": "192.168.1.50",
        "firmwareVersion": "4.63.22",
        "isConnected": True,
        "isRecording": True,
        "recordingMode": "always",
        "micVolume": 100,
        "speakerVolume": 80,
    }


@pytest.fixture
def sample_sensor() -> dict[str, Any]:
    """Return sample sensor data."""
    return {
        "id": "sensor-123",
        "mac": "22:33:44:55:66:77",
        "name": "Front Door Sensor",
        "type": "door",
        "isConnected": True,
        "isOpened": False,
        "batteryLevel": 95,
    }
