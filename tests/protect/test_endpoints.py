"""Tests for UniFi Protect endpoint methods."""

from __future__ import annotations

import re

import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth
from unifi_official_api.protect import LightMode, RecordingMode, UniFiProtectClient


class TestCamerasEndpoint:
    """Tests for cameras endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_cameras_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a camera."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1",
                payload={"data": {"id": "cam-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Updated"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                camera = await client.cameras.update("host-123", "site-1", "cam-1", name="Updated")
                assert camera.name == "Updated"

    async def test_cameras_set_recording_mode(self, auth: ApiKeyAuth) -> None:
        """Test setting camera recording mode."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1",
                payload={
                    "data": {"id": "cam-1", "mac": "aa:bb:cc:dd:ee:ff", "recordingMode": "always"}
                },
            )

            async with UniFiProtectClient(auth=auth) as client:
                camera = await client.cameras.set_recording_mode(
                    "host-123", "site-1", "cam-1", RecordingMode.ALWAYS
                )
                assert camera.id == "cam-1"

    async def test_cameras_get_snapshot(self, auth: ApiKeyAuth) -> None:
        """Test getting camera snapshot."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/snapshot",
                body=b"fake-image-bytes",
                content_type="image/jpeg",
            )

            async with UniFiProtectClient(auth=auth) as client:
                snapshot = await client.cameras.get_snapshot("host-123", "site-1", "cam-1")
                assert snapshot == b"fake-image-bytes"

    async def test_cameras_restart(self, auth: ApiKeyAuth) -> None:
        """Test restarting a camera."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/restart",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.restart("host-123", "site-1", "cam-1")
                assert result is True

    async def test_cameras_ptz_move(self, auth: ApiKeyAuth) -> None:
        """Test PTZ move."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/ptz/move",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.ptz_move(
                    "host-123", "site-1", "cam-1", pan=10, tilt=5, zoom=2
                )
                assert result is True


class TestSensorsEndpoint:
    """Tests for sensors endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_sensors_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific sensor."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": {"id": "sensor-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Door"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                sensor = await client.sensors.get("host-123", "site-1", "sensor-1")
                assert sensor.id == "sensor-1"

    async def test_sensors_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a sensor."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": {"id": "sensor-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Updated"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                sensor = await client.sensors.update(
                    "host-123", "site-1", "sensor-1", name="Updated"
                )
                assert sensor.name == "Updated"

    async def test_sensors_set_status_led(self, auth: ApiKeyAuth) -> None:
        """Test setting sensor status LED."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": {"id": "sensor-1", "mac": "aa:bb:cc:dd:ee:ff"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                sensor = await client.sensors.set_status_led(
                    "host-123", "site-1", "sensor-1", enabled=True
                )
                assert sensor.id == "sensor-1"

    async def test_sensors_set_motion_sensitivity(self, auth: ApiKeyAuth) -> None:
        """Test setting sensor motion sensitivity."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": {"id": "sensor-1", "mac": "aa:bb:cc:dd:ee:ff"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                sensor = await client.sensors.set_motion_sensitivity(
                    "host-123", "site-1", "sensor-1", sensitivity=50
                )
                assert sensor.id == "sensor-1"


class TestLightsEndpoint:
    """Tests for lights endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_lights_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing lights."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights",
                payload={"data": [{"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Flood"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                lights = await client.lights.get_all("host-123", "site-1")
                assert len(lights) == 1
                assert lights[0].name == "Flood"

    async def test_lights_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific light."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": {"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Flood"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                light = await client.lights.get("host-123", "site-1", "light-1")
                assert light.id == "light-1"

    async def test_lights_turn_on(self, auth: ApiKeyAuth) -> None:
        """Test turning on a light."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": {"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "isLightOn": True}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                light = await client.lights.turn_on("host-123", "site-1", "light-1")
                assert light.is_light_on is True

    async def test_lights_turn_off(self, auth: ApiKeyAuth) -> None:
        """Test turning off a light."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": {"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "isLightOn": False}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                light = await client.lights.turn_off("host-123", "site-1", "light-1")
                assert light.is_light_on is False

    async def test_lights_set_mode(self, auth: ApiKeyAuth) -> None:
        """Test setting light mode."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={
                    "data": {"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "lightMode": "motion"}
                },
            )

            async with UniFiProtectClient(auth=auth) as client:
                light = await client.lights.set_mode(
                    "host-123", "site-1", "light-1", LightMode.MOTION
                )
                assert light.id == "light-1"

    async def test_lights_set_brightness(self, auth: ApiKeyAuth) -> None:
        """Test setting light brightness."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": {"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "brightness": 75}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                light = await client.lights.set_brightness("host-123", "site-1", "light-1", 75)
                assert light.id == "light-1"


class TestChimesEndpoint:
    """Tests for chimes endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_chimes_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing chimes."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes",
                payload={
                    "data": [{"id": "chime-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Doorbell"}]
                },
            )

            async with UniFiProtectClient(auth=auth) as client:
                chimes = await client.chimes.get_all("host-123", "site-1")
                assert len(chimes) == 1
                assert chimes[0].name == "Doorbell"

    async def test_chimes_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific chime."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1",
                payload={"data": {"id": "chime-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Doorbell"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                chime = await client.chimes.get("host-123", "site-1", "chime-1")
                assert chime.id == "chime-1"

    async def test_chimes_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a chime."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1",
                payload={"data": {"id": "chime-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Updated"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                chime = await client.chimes.update("host-123", "site-1", "chime-1", name="Updated")
                assert chime.name == "Updated"

    async def test_chimes_set_volume(self, auth: ApiKeyAuth) -> None:
        """Test setting chime volume."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1",
                payload={"data": {"id": "chime-1", "mac": "aa:bb:cc:dd:ee:ff", "volume": 80}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                chime = await client.chimes.set_volume("host-123", "site-1", "chime-1", 80)
                assert chime.id == "chime-1"

    async def test_chimes_play(self, auth: ApiKeyAuth) -> None:
        """Test playing a chime."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1/play",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.chimes.play("host-123", "site-1", "chime-1")
                assert result is True


class TestNVREndpoint:
    """Tests for NVR endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_nvr_get(self, auth: ApiKeyAuth) -> None:
        """Test getting NVR info."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={"data": {"id": "nvr-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "NVR"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                nvr = await client.nvr.get("host-123", "site-1")
                assert nvr.id == "nvr-1"

    async def test_nvr_update(self, auth: ApiKeyAuth) -> None:
        """Test updating NVR."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={
                    "data": {"id": "nvr-1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Updated NVR"}
                },
            )

            async with UniFiProtectClient(auth=auth) as client:
                nvr = await client.nvr.update("host-123", "site-1", name="Updated NVR")
                assert nvr.name == "Updated NVR"

    async def test_nvr_restart(self, auth: ApiKeyAuth) -> None:
        """Test restarting NVR."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr/restart",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.nvr.restart("host-123", "site-1")
                assert result is True

    async def test_nvr_set_recording_retention(self, auth: ApiKeyAuth) -> None:
        """Test setting NVR recording retention."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={
                    "data": {
                        "id": "nvr-1", "mac": "aa:bb:cc:dd:ee:ff", "recordingRetentionDays": 30
                    }
                },
            )

            async with UniFiProtectClient(auth=auth) as client:
                nvr = await client.nvr.set_recording_retention("host-123", "site-1", 30)
                assert nvr.id == "nvr-1"


class TestLiveViewsEndpoint:
    """Tests for live views endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_liveviews_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing live views."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews",
                payload={"data": [{"id": "lv-1", "name": "Main View", "layout": 4}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                liveviews = await client.liveviews.get_all("host-123", "site-1")
                assert len(liveviews) == 1
                assert liveviews[0].name == "Main View"

    async def test_liveviews_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific live view."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-1",
                payload={"data": {"id": "lv-1", "name": "Main View", "layout": 4}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                liveview = await client.liveviews.get("host-123", "site-1", "lv-1")
                assert liveview.id == "lv-1"

    async def test_liveviews_create(self, auth: ApiKeyAuth) -> None:
        """Test creating a live view."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews",
                payload={"data": {"id": "lv-2", "name": "New View", "layout": 4}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                liveview = await client.liveviews.create(
                    "host-123", "site-1", name="New View", layout=4
                )
                assert liveview.name == "New View"

    async def test_liveviews_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a live view."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-1",
                payload={"data": {"id": "lv-1", "name": "Updated View", "layout": 9}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                liveview = await client.liveviews.update(
                    "host-123", "site-1", "lv-1", name="Updated View"
                )
                assert liveview.name == "Updated View"

    async def test_liveviews_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a live view."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-1",
                status=204,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.liveviews.delete("host-123", "site-1", "lv-1")
                assert result is True


class TestEventsEndpoint:
    """Tests for events endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_events_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing events."""
        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/events.*"),
                payload={"data": [{"id": "event-1", "type": "motion"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                events = await client.events.get_all("host-123", "site-1")
                assert len(events) == 1
                assert events[0].id == "event-1"

    async def test_events_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific event."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/events/event-1",
                payload={"data": {"id": "event-1", "type": "motion"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                event = await client.events.get("host-123", "site-1", "event-1")
                assert event.id == "event-1"

    async def test_events_get_thumbnail(self, auth: ApiKeyAuth) -> None:
        """Test getting event thumbnail."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/events/event-1/thumbnail",
                body=b"thumbnail-bytes",
                content_type="image/jpeg",
            )

            async with UniFiProtectClient(auth=auth) as client:
                thumbnail = await client.events.get_thumbnail("host-123", "site-1", "event-1")
                assert thumbnail == b"thumbnail-bytes"

    async def test_events_get_heatmap(self, auth: ApiKeyAuth) -> None:
        """Test getting event heatmap."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/events/event-1/heatmap",
                body=b"heatmap-bytes",
                content_type="image/png",
            )

            async with UniFiProtectClient(auth=auth) as client:
                heatmap = await client.events.get_heatmap("host-123", "site-1", "event-1")
                assert heatmap == b"heatmap-bytes"

    async def test_events_list_motion_events(self, auth: ApiKeyAuth) -> None:
        """Test listing motion events."""
        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/events.*"),
                payload={"data": [{"id": "event-1", "type": "motion"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                events = await client.events.list_motion_events("host-123", "site-1")
                assert len(events) == 1

    async def test_events_list_smart_detect_events(self, auth: ApiKeyAuth) -> None:
        """Test listing smart detect events."""
        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/events.*"),
                payload={"data": [{"id": "event-1", "type": "smartDetect"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                events = await client.events.list_smart_detect_events("host-123", "site-1")
                assert len(events) == 1


class TestProtectClientBinary:
    """Tests for Protect client binary methods."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_get_binary(self, auth: ApiKeyAuth) -> None:
        """Test getting binary content."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/snapshot",
                body=b"binary-content",
                content_type="application/octet-stream",
            )

            async with UniFiProtectClient(auth=auth) as client:
                content = await client.cameras.get_snapshot("host-123", "site-1", "cam-1")
                assert content == b"binary-content"
