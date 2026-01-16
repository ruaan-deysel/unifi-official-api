"""Tests for UniFi Protect client."""

from __future__ import annotations

from typing import Any

from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth
from unifi_official_api.protect import UniFiProtectClient


class TestUniFiProtectClient:
    """Tests for UniFiProtectClient."""

    async def test_client_creation(self, auth: ApiKeyAuth) -> None:
        """Test client creation."""
        async with UniFiProtectClient(auth=auth) as client:
            assert client.base_url.host == "api.ui.com"
            assert not client.closed

    async def test_client_close(self, auth: ApiKeyAuth) -> None:
        """Test client close."""
        client = UniFiProtectClient(auth=auth)
        assert not client.closed
        await client.close()
        assert client.closed

    async def test_endpoints_available(self, auth: ApiKeyAuth) -> None:
        """Test that all endpoints are available."""
        async with UniFiProtectClient(auth=auth) as client:
            assert client.cameras is not None
            assert client.sensors is not None
            assert client.lights is not None
            assert client.chimes is not None
            assert client.nvr is not None
            assert client.liveviews is not None
            assert client.events is not None


class TestCamerasEndpoint:
    """Tests for cameras endpoint."""

    async def test_list_cameras(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
        host_id: str,
        site_id: str,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test listing cameras."""
        mock_aioresponse.get(
            f"https://api.ui.com/ea/hosts/{host_id}/sites/{site_id}/cameras",
            payload={"data": [sample_camera]},
        )

        async with UniFiProtectClient(auth=auth) as client:
            cameras = await client.cameras.get_all(host_id, site_id)
            assert len(cameras) == 1
            assert cameras[0].id == "camera-123"
            assert cameras[0].name == "Front Door"
            assert cameras[0].is_recording is True

    async def test_get_camera(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
        host_id: str,
        site_id: str,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test getting a specific camera."""
        camera_id = sample_camera["id"]
        mock_aioresponse.get(
            f"https://api.ui.com/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}",
            payload={"data": sample_camera},
        )

        async with UniFiProtectClient(auth=auth) as client:
            camera = await client.cameras.get(host_id, site_id, camera_id)
            assert camera.id == camera_id
            assert camera.mic_volume == 100
            assert camera.speaker_volume == 80


class TestSensorsEndpoint:
    """Tests for sensors endpoint."""

    async def test_list_sensors(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
        host_id: str,
        site_id: str,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test listing sensors."""
        mock_aioresponse.get(
            f"https://api.ui.com/ea/hosts/{host_id}/sites/{site_id}/sensors",
            payload={"data": [sample_sensor]},
        )

        async with UniFiProtectClient(auth=auth) as client:
            sensors = await client.sensors.get_all(host_id, site_id)
            assert len(sensors) == 1
            assert sensors[0].id == "sensor-123"
            assert sensors[0].is_opened is False
            assert sensors[0].battery_level == 95
