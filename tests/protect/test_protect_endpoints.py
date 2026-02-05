"""Comprehensive tests for UniFi Protect endpoints with 100% coverage."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import pytest
from aioresponses import aioresponses

from unifi_official_api.protect import UniFiProtectClient
from unifi_official_api.protect.models import (
    EventType,
    FileType,
    LightMode,
    RecordingMode,
)


class TestCamerasEndpointComprehensive:
    """Comprehensive tests for cameras endpoint."""

    async def test_cameras_get_all_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test listing all cameras with data key response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras",
            payload={"data": [sample_camera, {**sample_camera, "id": "camera-456"}]},
        )

        cameras = await protect_client.cameras.get_all()
        assert len(cameras) == 2
        assert cameras[0].id == "camera-123"
        assert cameras[1].id == "camera-456"

    async def test_cameras_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test listing all cameras with direct list response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras",
            payload=[sample_camera],
        )

        cameras = await protect_client.cameras.get_all()
        assert len(cameras) == 1
        assert cameras[0].id == "camera-123"

    async def test_cameras_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing cameras with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras",
            payload={"data": []},
        )

        cameras = await protect_client.cameras.get_all()
        assert cameras == []

    async def test_cameras_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing cameras with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras",
            payload=None,
        )

        cameras = await protect_client.cameras.get_all()
        assert cameras == []

    async def test_cameras_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test getting a specific camera with data key."""
        camera_id = sample_camera["id"]
        mock_aioresponse.get(
            f"https://192.168.1.1/proxy/protect/integration/v1/cameras/{camera_id}",
            payload={"data": sample_camera},
        )

        camera = await protect_client.cameras.get(camera_id)
        assert camera.id == camera_id
        assert camera.name == "Front Door"

    async def test_cameras_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test getting a camera with list response."""
        camera_id = sample_camera["id"]
        mock_aioresponse.get(
            f"https://192.168.1.1/proxy/protect/integration/v1/cameras/{camera_id}",
            payload={"data": [sample_camera]},
        )

        camera = await protect_client.cameras.get(camera_id)
        assert camera.id == camera_id

    async def test_cameras_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a camera that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Camera cam-999 not found"):
            await protect_client.cameras.get("cam-999")

    async def test_cameras_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test updating a camera successfully."""
        camera_id = sample_camera["id"]
        updated_camera = {**sample_camera, "name": "Back Door", "micVolume": 50}
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/cameras/{camera_id}",
            payload={"data": updated_camera},
        )

        camera = await protect_client.cameras.update(
            camera_id, name="Back Door", micVolume=50
        )
        assert camera.name == "Back Door"
        assert camera.mic_volume == 50

    async def test_cameras_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test camera update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update camera"):
            await protect_client.cameras.update("cam-1", name="Test")

    async def test_cameras_set_recording_mode(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting camera recording mode."""
        camera_id = sample_camera["id"]
        updated_camera = {**sample_camera, "recordingMode": "motion"}
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/cameras/{camera_id}",
            payload={"data": updated_camera},
        )

        camera = await protect_client.cameras.set_recording_mode(
            camera_id, RecordingMode.MOTION
        )
        assert camera.id == camera_id

    async def test_cameras_get_snapshot_with_params(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting camera snapshot with width and height."""
        mock_aioresponse.get(
            re.compile(
                r"https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/snapshot.*"
            ),
            body=b"fake_snapshot_data",
        )

        snapshot = await protect_client.cameras.get_snapshot(
            "cam-1", width=640, height=480
        )
        assert snapshot == b"fake_snapshot_data"

    async def test_cameras_get_snapshot_without_params(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting camera snapshot without parameters."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/snapshot",
            body=b"fake_snapshot",
        )

        snapshot = await protect_client.cameras.get_snapshot("cam-1")
        assert snapshot == b"fake_snapshot"

    async def test_cameras_restart(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test restarting a camera."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/restart",
            payload={},
        )

        result = await protect_client.cameras.restart("cam-1")
        assert result is True

    async def test_cameras_set_microphone_volume_valid(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting microphone volume with valid value."""
        camera_id = sample_camera["id"]
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/cameras/{camera_id}",
            payload={"data": {**sample_camera, "micVolume": 75}},
        )

        camera = await protect_client.cameras.set_microphone_volume(camera_id, 75)
        assert camera.mic_volume == 75

    async def test_cameras_set_microphone_volume_invalid_low(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting microphone volume with invalid value (too low)."""
        with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
            await protect_client.cameras.set_microphone_volume("cam-1", -1)

    async def test_cameras_set_microphone_volume_invalid_high(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting microphone volume with invalid value (too high)."""
        with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
            await protect_client.cameras.set_microphone_volume("cam-1", 101)

    async def test_cameras_set_speaker_volume_valid(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting speaker volume with valid value."""
        camera_id = sample_camera["id"]
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/cameras/{camera_id}",
            payload={"data": {**sample_camera, "speakerVolume": 60}},
        )

        camera = await protect_client.cameras.set_speaker_volume(camera_id, 60)
        assert camera.speaker_volume == 60

    async def test_cameras_set_speaker_volume_invalid(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting speaker volume with invalid value."""
        with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
            await protect_client.cameras.set_speaker_volume("cam-1", 150)

    async def test_cameras_ptz_move_all_params(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test PTZ move with all parameters."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/ptz/move",
            payload={},
        )

        result = await protect_client.cameras.ptz_move(
            "cam-1", pan=0.5, tilt=-0.3, zoom=0.8
        )
        assert result is True

    async def test_cameras_ptz_move_partial_params(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test PTZ move with partial parameters."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/ptz/move",
            payload={},
        )

        result = await protect_client.cameras.ptz_move("cam-1", pan=0.5)
        assert result is True

    async def test_cameras_ptz_goto_preset(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test PTZ goto preset."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/ptz/goto/preset-1",
            payload={},
        )

        result = await protect_client.cameras.ptz_goto_preset("cam-1", "preset-1")
        assert result is True

    async def test_cameras_ptz_patrol_start_valid_slot(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test starting PTZ patrol with valid slot."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/ptz/patrol/start/2",
            payload={},
        )

        result = await protect_client.cameras.ptz_patrol_start("cam-1", 2)
        assert result is True

    async def test_cameras_ptz_patrol_start_invalid_slot_low(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test starting PTZ patrol with invalid slot (too low)."""
        with pytest.raises(ValueError, match="Slot must be between 0 and 4"):
            await protect_client.cameras.ptz_patrol_start("cam-1", -1)

    async def test_cameras_ptz_patrol_start_invalid_slot_high(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test starting PTZ patrol with invalid slot (too high)."""
        with pytest.raises(ValueError, match="Slot must be between 0 and 4"):
            await protect_client.cameras.ptz_patrol_start("cam-1", 5)

    async def test_cameras_ptz_patrol_stop(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test stopping PTZ patrol."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/ptz/patrol/stop",
            payload={},
        )

        result = await protect_client.cameras.ptz_patrol_stop("cam-1")
        assert result is True

    async def test_cameras_create_rtsps_stream_default_quality(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating RTSPS stream with default quality."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream",
            payload={"data": {"high": "rtsps://192.168.1.1:7441/stream"}},
        )

        stream = await protect_client.cameras.create_rtsps_stream("cam-1")
        assert stream.high == "rtsps://192.168.1.1:7441/stream"

    async def test_cameras_create_rtsps_stream_custom_qualities(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating RTSPS stream with custom qualities."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream",
            payload={
                "data": {
                    "high": "rtsps://192.168.1.1:7441/h",
                    "medium": "rtsps://192.168.1.1:7441/m",
                }
            },
        )

        stream = await protect_client.cameras.create_rtsps_stream(
            "cam-1", qualities=["high", "medium"]
        )
        assert stream.high == "rtsps://192.168.1.1:7441/h"
        assert stream.medium == "rtsps://192.168.1.1:7441/m"

    async def test_cameras_create_rtsps_stream_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating RTSPS stream failure."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to create RTSPS stream"):
            await protect_client.cameras.create_rtsps_stream("cam-1")

    async def test_cameras_get_rtsps_stream(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting RTSPS stream."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream",
            payload={"data": {"url": "rtsps://192.168.1.1:7441/stream"}},
        )

        stream = await protect_client.cameras.get_rtsps_stream("cam-1")
        assert stream.url == "rtsps://192.168.1.1:7441/stream"

    async def test_cameras_get_rtsps_stream_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting RTSPS stream that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="RTSPS stream not found"):
            await protect_client.cameras.get_rtsps_stream("cam-1")

    async def test_cameras_delete_rtsps_stream_default_quality(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test deleting RTSPS stream with default quality."""
        mock_aioresponse.delete(
            re.compile(
                r"https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream.*"
            ),
            status=204,
        )

        result = await protect_client.cameras.delete_rtsps_stream("cam-1")
        assert result is True

    async def test_cameras_delete_rtsps_stream_custom_qualities(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test deleting RTSPS stream with custom qualities."""
        mock_aioresponse.delete(
            re.compile(
                r"https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/rtsps-stream.*"
            ),
            status=204,
        )

        result = await protect_client.cameras.delete_rtsps_stream(
            "cam-1", qualities=["high", "low"]
        )
        assert result is True

    async def test_cameras_create_talkback_session_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating talkback session successfully."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/talkback-session",
            payload={
                "data": {
                    "url": "rtp://192.168.1.1:7004",
                    "codec": "opus",
                    "samplingRate": 24000,
                    "bitsPerSample": 16,
                }
            },
        )

        session = await protect_client.cameras.create_talkback_session("cam-1")
        assert session.url == "rtp://192.168.1.1:7004"
        assert session.codec == "opus"
        assert session.sampling_rate == 24000

    async def test_cameras_create_talkback_session_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating talkback session failure."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/talkback-session",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to create talkback session"):
            await protect_client.cameras.create_talkback_session("cam-1")

    async def test_cameras_disable_mic_permanently_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test permanently disabling microphone successfully."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/disable-mic-permanently",
            payload={"data": {**sample_camera, "isMicEnabled": False}},
        )

        camera = await protect_client.cameras.disable_mic_permanently("cam-1")
        assert camera is not None

    async def test_cameras_disable_mic_permanently_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test permanently disabling microphone failure."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1/disable-mic-permanently",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to disable microphone"):
            await protect_client.cameras.disable_mic_permanently("cam-1")

    async def test_cameras_set_hdr_mode_auto(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting HDR mode to auto."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1",
            payload={"data": {**sample_camera, "hdrType": "auto"}},
        )

        camera = await protect_client.cameras.set_hdr_mode("cam-1", "auto")
        assert camera is not None

    async def test_cameras_set_hdr_mode_on(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting HDR mode to on."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1",
            payload={"data": {**sample_camera, "hdrType": "on"}},
        )

        camera = await protect_client.cameras.set_hdr_mode("cam-1", "on")
        assert camera is not None

    async def test_cameras_set_hdr_mode_off(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting HDR mode to off."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1",
            payload={"data": {**sample_camera, "hdrType": "off"}},
        )

        camera = await protect_client.cameras.set_hdr_mode("cam-1", "off")
        assert camera is not None

    async def test_cameras_set_hdr_mode_invalid(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting HDR mode with invalid value."""
        with pytest.raises(ValueError, match="HDR mode must be 'auto', 'on', or 'off'"):
            await protect_client.cameras.set_hdr_mode("cam-1", "invalid")

    async def test_cameras_set_video_mode(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_camera: dict[str, Any],
    ) -> None:
        """Test setting video mode."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/cameras/cam-1",
            payload={"data": {**sample_camera, "videoMode": "highFps"}},
        )

        camera = await protect_client.cameras.set_video_mode("cam-1", "highFps")
        assert camera is not None


class TestSensorsEndpointComprehensive:
    """Comprehensive tests for sensors endpoint."""

    async def test_sensors_get_all_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test listing all sensors with data key response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/sensors",
            payload={"data": [sample_sensor, {**sample_sensor, "id": "sensor-456"}]},
        )

        sensors = await protect_client.sensors.get_all()
        assert len(sensors) == 2
        assert sensors[0].id == "sensor-123"
        assert sensors[1].id == "sensor-456"

    async def test_sensors_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test listing all sensors with direct list response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/sensors",
            payload=[sample_sensor],
        )

        sensors = await protect_client.sensors.get_all()
        assert len(sensors) == 1
        assert sensors[0].id == "sensor-123"

    async def test_sensors_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing sensors with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/sensors",
            payload={"data": []},
        )

        sensors = await protect_client.sensors.get_all()
        assert sensors == []

    async def test_sensors_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing sensors with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/sensors",
            payload=None,
        )

        sensors = await protect_client.sensors.get_all()
        assert sensors == []

    async def test_sensors_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test getting a specific sensor with data key."""
        sensor_id = sample_sensor["id"]
        mock_aioresponse.get(
            f"https://192.168.1.1/proxy/protect/integration/v1/sensors/{sensor_id}",
            payload={"data": sample_sensor},
        )

        sensor = await protect_client.sensors.get(sensor_id)
        assert sensor.id == sensor_id
        assert sensor.name == "Front Door Sensor"

    async def test_sensors_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test getting a sensor with list response."""
        sensor_id = sample_sensor["id"]
        mock_aioresponse.get(
            f"https://192.168.1.1/proxy/protect/integration/v1/sensors/{sensor_id}",
            payload={"data": [sample_sensor]},
        )

        sensor = await protect_client.sensors.get(sensor_id)
        assert sensor.id == sensor_id

    async def test_sensors_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a sensor that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/sensors/sensor-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Sensor sensor-999 not found"):
            await protect_client.sensors.get("sensor-999")

    async def test_sensors_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test updating a sensor successfully."""
        sensor_id = sample_sensor["id"]
        updated_sensor = {**sample_sensor, "name": "Back Door Sensor"}
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/sensors/{sensor_id}",
            payload={"data": updated_sensor},
        )

        sensor = await protect_client.sensors.update(sensor_id, name="Back Door Sensor")
        assert sensor.name == "Back Door Sensor"

    async def test_sensors_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test sensor update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/sensors/sensor-1",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update sensor"):
            await protect_client.sensors.update("sensor-1", name="Test")

    async def test_sensors_set_status_led(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test setting sensor status LED."""
        sensor_id = sample_sensor["id"]
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/sensors/{sensor_id}",
            payload={"data": {**sample_sensor, "openStatusLedEnabled": True}},
        )

        sensor = await protect_client.sensors.set_status_led(sensor_id, True)
        assert sensor is not None

    async def test_sensors_set_motion_sensitivity_valid(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
        sample_sensor: dict[str, Any],
    ) -> None:
        """Test setting motion sensitivity with valid value."""
        sensor_id = sample_sensor["id"]
        mock_aioresponse.patch(
            f"https://192.168.1.1/proxy/protect/integration/v1/sensors/{sensor_id}",
            payload={"data": {**sample_sensor, "motionSensitivity": 75}},
        )

        sensor = await protect_client.sensors.set_motion_sensitivity(sensor_id, 75)
        assert sensor is not None

    async def test_sensors_set_motion_sensitivity_invalid_low(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting motion sensitivity with invalid value (too low)."""
        with pytest.raises(ValueError, match="Sensitivity must be between 0 and 100"):
            await protect_client.sensors.set_motion_sensitivity("sensor-1", -1)

    async def test_sensors_set_motion_sensitivity_invalid_high(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting motion sensitivity with invalid value (too high)."""
        with pytest.raises(ValueError, match="Sensitivity must be between 0 and 100"):
            await protect_client.sensors.set_motion_sensitivity("sensor-1", 101)


class TestLightsEndpointComprehensive:
    """Comprehensive tests for lights endpoint."""

    async def test_lights_get_all_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all lights with data key response."""
        lights_data = [
            {"id": "light-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Light 1"},
            {"id": "light-2", "mac": "11:22:33:44:55:66", "name": "Light 2"},
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights",
            payload={"data": lights_data},
        )

        lights = await protect_client.lights.get_all()
        assert len(lights) == 2
        assert lights[0].id == "light-1"
        assert lights[1].id == "light-2"

    async def test_lights_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all lights with direct list response."""
        lights_data = [{"id": "light-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Light 1"}]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights",
            payload=lights_data,
        )

        lights = await protect_client.lights.get_all()
        assert len(lights) == 1
        assert lights[0].id == "light-1"

    async def test_lights_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing lights with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights",
            payload={"data": []},
        )

        lights = await protect_client.lights.get_all()
        assert lights == []

    async def test_lights_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing lights with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights",
            payload=None,
        )

        lights = await protect_client.lights.get_all()
        assert lights == []

    async def test_lights_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a specific light with data key."""
        light_data = {"id": "light-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Test Light"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": light_data},
        )

        light = await protect_client.lights.get("light-1")
        assert light.id == "light-1"
        assert light.name == "Test Light"

    async def test_lights_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a light with list response."""
        light_data = {"id": "light-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Test Light"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": [light_data]},
        )

        light = await protect_client.lights.get("light-1")
        assert light.id == "light-1"

    async def test_lights_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a light that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Light light-999 not found"):
            await protect_client.lights.get("light-999")

    async def test_lights_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test updating a light successfully."""
        light_data = {"id": "light-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Updated Light"}
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": light_data},
        )

        light = await protect_client.lights.update("light-1", name="Updated Light")
        assert light.name == "Updated Light"

    async def test_lights_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test light update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update light"):
            await protect_client.lights.update("light-1", name="Test")

    async def test_lights_turn_on(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test turning on a light."""
        light_data = {
            "id": "light-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "lightMode": "on",
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": light_data},
        )

        light = await protect_client.lights.turn_on("light-1")
        assert light is not None

    async def test_lights_turn_off(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test turning off a light."""
        light_data = {
            "id": "light-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "lightMode": "off",
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": light_data},
        )

        light = await protect_client.lights.turn_off("light-1")
        assert light is not None

    async def test_lights_set_mode(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test setting light mode."""
        light_data = {
            "id": "light-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "lightMode": "motion",
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": light_data},
        )

        light = await protect_client.lights.set_mode("light-1", LightMode.MOTION)
        assert light is not None

    async def test_lights_set_brightness_valid(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test setting brightness with valid value."""
        light_data = {
            "id": "light-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "brightness": 75,
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/lights/light-1",
            payload={"data": light_data},
        )

        light = await protect_client.lights.set_brightness("light-1", 75)
        assert light is not None

    async def test_lights_set_brightness_invalid_low(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting brightness with invalid value (too low)."""
        with pytest.raises(ValueError, match="Brightness must be between 0 and 100"):
            await protect_client.lights.set_brightness("light-1", -1)

    async def test_lights_set_brightness_invalid_high(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting brightness with invalid value (too high)."""
        with pytest.raises(ValueError, match="Brightness must be between 0 and 100"):
            await protect_client.lights.set_brightness("light-1", 101)


class TestChimesEndpointComprehensive:
    """Comprehensive tests for chimes endpoint."""

    async def test_chimes_get_all_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all chimes with data key response."""
        chimes_data = [
            {"id": "chime-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Chime 1"},
            {"id": "chime-2", "mac": "11:22:33:44:55:66", "name": "Chime 2"},
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes",
            payload={"data": chimes_data},
        )

        chimes = await protect_client.chimes.get_all()
        assert len(chimes) == 2
        assert chimes[0].id == "chime-1"
        assert chimes[1].id == "chime-2"

    async def test_chimes_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all chimes with direct list response."""
        chimes_data = [{"id": "chime-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Chime 1"}]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes",
            payload=chimes_data,
        )

        chimes = await protect_client.chimes.get_all()
        assert len(chimes) == 1
        assert chimes[0].id == "chime-1"

    async def test_chimes_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing chimes with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes",
            payload={"data": []},
        )

        chimes = await protect_client.chimes.get_all()
        assert chimes == []

    async def test_chimes_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing chimes with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes",
            payload=None,
        )

        chimes = await protect_client.chimes.get_all()
        assert chimes == []

    async def test_chimes_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a specific chime with data key."""
        chime_data = {"id": "chime-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Test Chime"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-1",
            payload={"data": chime_data},
        )

        chime = await protect_client.chimes.get("chime-1")
        assert chime.id == "chime-1"
        assert chime.name == "Test Chime"

    async def test_chimes_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a chime with list response."""
        chime_data = {"id": "chime-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Test Chime"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-1",
            payload={"data": [chime_data]},
        )

        chime = await protect_client.chimes.get("chime-1")
        assert chime.id == "chime-1"

    async def test_chimes_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a chime that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Chime chime-999 not found"):
            await protect_client.chimes.get("chime-999")

    async def test_chimes_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test updating a chime successfully."""
        chime_data = {
            "id": "chime-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "name": "Updated Chime",
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-1",
            payload={"data": chime_data},
        )

        chime = await protect_client.chimes.update("chime-1", name="Updated Chime")
        assert chime.name == "Updated Chime"

    async def test_chimes_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test chime update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-1",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update chime"):
            await protect_client.chimes.update("chime-1", name="Test")

    async def test_chimes_set_volume_valid(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test setting chime volume with valid value."""
        chime_data = {
            "id": "chime-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "volume": 50,
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-1",
            payload={"data": chime_data},
        )

        chime = await protect_client.chimes.set_volume("chime-1", 50)
        assert chime is not None

    async def test_chimes_set_volume_invalid_low(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting chime volume with invalid value (too low)."""
        with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
            await protect_client.chimes.set_volume("chime-1", -1)

    async def test_chimes_set_volume_invalid_high(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting chime volume with invalid value (too high)."""
        with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
            await protect_client.chimes.set_volume("chime-1", 101)

    async def test_chimes_play(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test playing chime."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/chimes/chime-1/play",
            payload={},
        )

        result = await protect_client.chimes.play("chime-1")
        assert result is True


class TestNVREndpointComprehensive:
    """Comprehensive tests for NVR endpoint."""

    async def test_nvr_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting NVR with data key."""
        nvr_data = {"id": "nvr-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Test NVR"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/nvrs",
            payload={"data": nvr_data},
        )

        nvr = await protect_client.nvr.get()
        assert nvr.id == "nvr-1"
        assert nvr.name == "Test NVR"

    async def test_nvr_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting NVR with list response."""
        nvr_data = {"id": "nvr-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Test NVR"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/nvrs",
            payload={"data": [nvr_data]},
        )

        nvr = await protect_client.nvr.get()
        assert nvr.id == "nvr-1"

    async def test_nvr_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting NVR that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/nvrs",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="NVR not found"):
            await protect_client.nvr.get()

    async def test_nvr_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test updating NVR successfully."""
        nvr_data = {"id": "nvr-1", "mac": "AA:BB:CC:DD:EE:FF", "name": "Updated NVR"}
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/nvr",
            payload={"data": nvr_data},
        )

        nvr = await protect_client.nvr.update(name="Updated NVR")
        assert nvr.name == "Updated NVR"

    async def test_nvr_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test NVR update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/nvr",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update NVR"):
            await protect_client.nvr.update(name="Test")

    async def test_nvr_restart(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test restarting NVR."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/nvr/restart",
            payload={},
        )

        result = await protect_client.nvr.restart()
        assert result is True

    async def test_nvr_set_recording_retention_valid(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test setting recording retention with valid value."""
        nvr_data = {
            "id": "nvr-1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "recordingRetentionDays": 30,
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/nvr",
            payload={"data": nvr_data},
        )

        nvr = await protect_client.nvr.set_recording_retention(30)
        assert nvr is not None

    async def test_nvr_set_recording_retention_invalid(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test setting recording retention with invalid value."""
        with pytest.raises(ValueError, match="Retention days must be at least 1"):
            await protect_client.nvr.set_recording_retention(0)


class TestLiveViewsEndpointComprehensive:
    """Comprehensive tests for liveviews endpoint."""

    async def test_liveviews_get_all_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all liveviews with data key response."""
        liveviews_data = [
            {"id": "lv-1", "name": "Main View", "layout": 4},
            {"id": "lv-2", "name": "Secondary View", "layout": 9},
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload={"data": liveviews_data},
        )

        liveviews = await protect_client.liveviews.get_all()
        assert len(liveviews) == 2
        assert liveviews[0].id == "lv-1"
        assert liveviews[1].id == "lv-2"

    async def test_liveviews_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all liveviews with direct list response."""
        liveviews_data = [{"id": "lv-1", "name": "Main View", "layout": 4}]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload=liveviews_data,
        )

        liveviews = await protect_client.liveviews.get_all()
        assert len(liveviews) == 1
        assert liveviews[0].id == "lv-1"

    async def test_liveviews_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing liveviews with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload={"data": []},
        )

        liveviews = await protect_client.liveviews.get_all()
        assert liveviews == []

    async def test_liveviews_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing liveviews with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload=None,
        )

        liveviews = await protect_client.liveviews.get_all()
        assert liveviews == []

    async def test_liveviews_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a specific liveview with data key."""
        liveview_data = {"id": "lv-1", "name": "Main View", "layout": 4}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews/lv-1",
            payload={"data": liveview_data},
        )

        liveview = await protect_client.liveviews.get("lv-1")
        assert liveview.id == "lv-1"
        assert liveview.name == "Main View"

    async def test_liveviews_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a liveview with list response."""
        liveview_data = {"id": "lv-1", "name": "Main View", "layout": 4}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews/lv-1",
            payload={"data": [liveview_data]},
        )

        liveview = await protect_client.liveviews.get("lv-1")
        assert liveview.id == "lv-1"

    async def test_liveviews_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a liveview that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews/lv-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="LiveView lv-999 not found"):
            await protect_client.liveviews.get("lv-999")

    async def test_liveviews_create_basic(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating a liveview with basic parameters."""
        liveview_data = {"id": "lv-1", "name": "New View", "layout": 4}
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload={"data": liveview_data},
        )

        liveview = await protect_client.liveviews.create(name="New View", layout=4)
        assert liveview.name == "New View"
        assert liveview.layout == 4

    async def test_liveviews_create_with_slots(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating a liveview with slots."""
        liveview_data = {
            "id": "lv-1",
            "name": "New View",
            "layout": 4,
            "slots": [{"cameraId": "cam-1", "position": 0}],
        }
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload={"data": liveview_data},
        )

        liveview = await protect_client.liveviews.create(
            name="New View",
            layout=4,
            slots=[{"cameraId": "cam-1", "position": 0}],
        )
        assert liveview.name == "New View"

    async def test_liveviews_create_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test creating a liveview failure."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to create live view"):
            await protect_client.liveviews.create(name="Test", layout=4)

    async def test_liveviews_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test updating a liveview successfully."""
        liveview_data = {"id": "lv-1", "name": "Updated View", "layout": 4}
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews/lv-1",
            payload={"data": liveview_data},
        )

        liveview = await protect_client.liveviews.update("lv-1", name="Updated View")
        assert liveview.name == "Updated View"

    async def test_liveviews_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test liveview update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews/lv-1",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update live view"):
            await protect_client.liveviews.update("lv-1", name="Test")

    async def test_liveviews_delete(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test deleting a liveview."""
        mock_aioresponse.delete(
            "https://192.168.1.1/proxy/protect/integration/v1/liveviews/lv-1",
            status=204,
        )

        result = await protect_client.liveviews.delete("lv-1")
        assert result is True


class TestViewersEndpointComprehensive:
    """Comprehensive tests for viewers endpoint."""

    async def test_viewers_get_all_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all viewers with data key response."""
        viewers_data = [
            {
                "id": "viewer-1",
                "modelKey": "viewer",
                "state": "CONNECTED",
                "name": "Viewer 1",
                "mac": "AA:BB:CC:DD:EE:FF",
                "streamLimit": 4,
            },
            {
                "id": "viewer-2",
                "modelKey": "viewer",
                "state": "CONNECTED",
                "name": "Viewer 2",
                "mac": "11:22:33:44:55:66",
                "streamLimit": 4,
            },
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers",
            payload={"data": viewers_data},
        )

        viewers = await protect_client.viewers.get_all()
        assert len(viewers) == 2
        assert viewers[0].id == "viewer-1"
        assert viewers[1].id == "viewer-2"

    async def test_viewers_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing all viewers with direct list response."""
        viewers_data = [
            {
                "id": "viewer-1",
                "modelKey": "viewer",
                "state": "CONNECTED",
                "name": "Viewer 1",
                "mac": "AA:BB:CC:DD:EE:FF",
                "streamLimit": 4,
            }
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers",
            payload=viewers_data,
        )

        viewers = await protect_client.viewers.get_all()
        assert len(viewers) == 1
        assert viewers[0].id == "viewer-1"

    async def test_viewers_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing viewers with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers",
            payload={"data": []},
        )

        viewers = await protect_client.viewers.get_all()
        assert viewers == []

    async def test_viewers_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing viewers with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers",
            payload=None,
        )

        viewers = await protect_client.viewers.get_all()
        assert viewers == []

    async def test_viewers_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a specific viewer with data key."""
        viewer_data = {
            "id": "viewer-1",
            "modelKey": "viewer",
            "state": "CONNECTED",
            "name": "Test Viewer",
            "mac": "AA:BB:CC:DD:EE:FF",
            "streamLimit": 4,
        }
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-1",
            payload={"data": viewer_data},
        )

        viewer = await protect_client.viewers.get("viewer-1")
        assert viewer.id == "viewer-1"
        assert viewer.name == "Test Viewer"

    async def test_viewers_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a viewer with list response."""
        viewer_data = {
            "id": "viewer-1",
            "modelKey": "viewer",
            "state": "CONNECTED",
            "name": "Test Viewer",
            "mac": "AA:BB:CC:DD:EE:FF",
            "streamLimit": 4,
        }
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-1",
            payload={"data": [viewer_data]},
        )

        viewer = await protect_client.viewers.get("viewer-1")
        assert viewer.id == "viewer-1"

    async def test_viewers_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a viewer that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Viewer viewer-999 not found"):
            await protect_client.viewers.get("viewer-999")

    async def test_viewers_update_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test updating a viewer successfully."""
        viewer_data = {
            "id": "viewer-1",
            "modelKey": "viewer",
            "state": "CONNECTED",
            "name": "Updated Viewer",
            "mac": "AA:BB:CC:DD:EE:FF",
            "streamLimit": 4,
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-1",
            payload={"data": viewer_data},
        )

        viewer = await protect_client.viewers.update("viewer-1", name="Updated Viewer")
        assert viewer.name == "Updated Viewer"

    async def test_viewers_update_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test viewer update failure."""
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-1",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to update viewer"):
            await protect_client.viewers.update("viewer-1", name="Test")

    async def test_viewers_set_liveview_with_id(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test setting liveview for a viewer."""
        viewer_data = {
            "id": "viewer-1",
            "modelKey": "viewer",
            "state": "CONNECTED",
            "name": "Viewer",
            "mac": "AA:BB:CC:DD:EE:FF",
            "liveview": "lv-1",
            "streamLimit": 4,
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-1",
            payload={"data": viewer_data},
        )

        viewer = await protect_client.viewers.set_liveview("viewer-1", "lv-1")
        assert viewer.liveview == "lv-1"

    async def test_viewers_set_liveview_unset(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test unsetting liveview for a viewer."""
        viewer_data = {
            "id": "viewer-1",
            "modelKey": "viewer",
            "state": "CONNECTED",
            "name": "Viewer",
            "mac": "AA:BB:CC:DD:EE:FF",
            "liveview": None,
            "streamLimit": 4,
        }
        mock_aioresponse.patch(
            "https://192.168.1.1/proxy/protect/integration/v1/viewers/viewer-1",
            payload={"data": viewer_data},
        )

        viewer = await protect_client.viewers.set_liveview("viewer-1", None)
        assert viewer.liveview is None


class TestEventsEndpointComprehensive:
    """Comprehensive tests for events endpoint."""

    async def test_events_get_all_basic(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing events with basic parameters."""
        events_data = [
            {"id": "ev-1", "type": "motion", "start": 1234567890000},
            {"id": "ev-2", "type": "smartDetect", "start": 1234567900000},
        ]
        mock_aioresponse.get(
            re.compile(
                r"https://192.168.1.1/proxy/protect/integration/v1/events\?limit=100"
            ),
            payload={"data": events_data},
        )

        events = await protect_client.events.get_all()
        assert len(events) == 2
        assert events[0].id == "ev-1"
        assert events[1].id == "ev-2"

    async def test_events_get_all_with_filters(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing events with filters."""
        events_data = [{"id": "ev-1", "type": "motion", "start": 1234567890000}]
        mock_aioresponse.get(
            re.compile(
                r"https://192.168.1.1/proxy/protect/integration/v1/events\?.*"
            ),
            payload={"data": events_data},
        )

        start = datetime.fromtimestamp(1234567890)
        end = datetime.fromtimestamp(1234567900)
        events = await protect_client.events.get_all(
            start=start,
            end=end,
            types=[EventType.MOTION],
            camera_ids=["cam-1", "cam-2"],
            limit=50,
        )
        assert len(events) == 1

    async def test_events_get_all_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing events with direct list response."""
        events_data = [{"id": "ev-1", "type": "motion", "start": 1234567890000}]
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload=events_data,
        )

        events = await protect_client.events.get_all()
        assert len(events) == 1

    async def test_events_get_all_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing events with empty response."""
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload={"data": []},
        )

        events = await protect_client.events.get_all()
        assert events == []

    async def test_events_get_all_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing events with None response."""
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload=None,
        )

        events = await protect_client.events.get_all()
        assert events == []

    async def test_events_get_with_data_key(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting a specific event with data key."""
        event_data = {"id": "ev-1", "type": "motion", "start": 1234567890000}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/events/ev-1",
            payload={"data": event_data},
        )

        event = await protect_client.events.get("ev-1")
        assert event.id == "ev-1"

    async def test_events_get_with_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting an event with list response."""
        event_data = {"id": "ev-1", "type": "motion", "start": 1234567890000}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/events/ev-1",
            payload={"data": [event_data]},
        )

        event = await protect_client.events.get("ev-1")
        assert event.id == "ev-1"

    async def test_events_get_not_found(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting an event that doesn't exist."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/events/ev-999",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Event ev-999 not found"):
            await protect_client.events.get("ev-999")

    async def test_events_get_thumbnail_with_params(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting event thumbnail with width and height."""
        mock_aioresponse.get(
            re.compile(
                r"https://192.168.1.1/proxy/protect/integration/v1/events/ev-1/thumbnail.*"
            ),
            body=b"fake_thumbnail_data",
        )

        thumbnail = await protect_client.events.get_thumbnail(
            "ev-1", width=320, height=240
        )
        assert thumbnail == b"fake_thumbnail_data"

    async def test_events_get_thumbnail_without_params(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting event thumbnail without parameters."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/events/ev-1/thumbnail",
            body=b"fake_thumbnail",
        )

        thumbnail = await protect_client.events.get_thumbnail("ev-1")
        assert thumbnail == b"fake_thumbnail"

    async def test_events_get_heatmap(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting event heatmap."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/events/ev-1/heatmap",
            body=b"fake_heatmap_data",
        )

        heatmap = await protect_client.events.get_heatmap("ev-1")
        assert heatmap == b"fake_heatmap_data"

    async def test_events_list_motion_events_basic(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing motion events with basic parameters."""
        events_data = [{"id": "ev-1", "type": "motion", "start": 1234567890000}]
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload={"data": events_data},
        )

        events = await protect_client.events.list_motion_events()
        assert len(events) == 1
        assert events[0].id == "ev-1"

    async def test_events_list_motion_events_with_filters(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing motion events with filters."""
        events_data = [{"id": "ev-1", "type": "motion", "start": 1234567890000}]
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload={"data": events_data},
        )

        start = datetime.fromtimestamp(1234567890)
        end = datetime.fromtimestamp(1234567900)
        events = await protect_client.events.list_motion_events(
            start=start, end=end, camera_ids=["cam-1"], limit=25
        )
        assert len(events) == 1

    async def test_events_list_smart_detect_events_basic(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing smart detect events with basic parameters."""
        events_data = [{"id": "ev-1", "type": "smartDetect", "start": 1234567890000}]
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload={"data": events_data},
        )

        events = await protect_client.events.list_smart_detect_events()
        assert len(events) == 1
        assert events[0].id == "ev-1"

    async def test_events_list_smart_detect_events_with_filters(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test listing smart detect events with filters."""
        events_data = [{"id": "ev-1", "type": "smartDetect", "start": 1234567890000}]
        mock_aioresponse.get(
            re.compile(r"https://192.168.1.1/proxy/protect/integration/v1/events.*"),
            payload={"data": events_data},
        )

        start = datetime.fromtimestamp(1234567890)
        events = await protect_client.events.list_smart_detect_events(
            start=start, camera_ids=["cam-1", "cam-2"], limit=10
        )
        assert len(events) == 1


class TestApplicationEndpointComprehensive:
    """Comprehensive tests for application endpoint."""

    async def test_application_get_info_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting application info successfully."""
        info_data = {"applicationVersion": "6.2.83", "firmwareVersion": "1.2.3"}
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/meta/info",
            payload={"data": info_data},
        )

        info = await protect_client.application.get_info()
        assert info.application_version == "6.2.83"

    async def test_application_get_info_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting application info failure."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/meta/info",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to get application info"):
            await protect_client.application.get_info()

    async def test_application_get_files_animations(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting animation files."""
        files_data = [
            {
                "name": "file-1",
                "type": "animations",
                "originalName": "logo.gif",
                "path": "/files/logo.gif",
            }
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/files/animations",
            payload={"data": files_data},
        )

        files = await protect_client.application.get_files(FileType.ANIMATIONS)
        assert len(files) == 1
        assert files[0].original_name == "logo.gif"

    async def test_application_get_files_list_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting files with direct list response."""
        files_data = [
            {
                "name": "file-1",
                "type": "animations",
                "originalName": "logo.gif",
                "path": "/files/logo.gif",
            }
        ]
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/files/animations",
            payload=files_data,
        )

        files = await protect_client.application.get_files()
        assert len(files) == 1

    async def test_application_get_files_empty(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting files with empty response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/files/animations",
            payload={"data": []},
        )

        files = await protect_client.application.get_files()
        assert files == []

    async def test_application_get_files_none_response(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting files with None response."""
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/files/animations",
            payload=None,
        )

        files = await protect_client.application.get_files()
        assert files == []

    async def test_application_upload_file_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test uploading a file successfully."""
        file_data_response = {
            "name": "file-new",
            "type": "animations",
            "originalName": "new.gif",
            "path": "/files/new.gif",
        }
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/files/animations",
            payload={"data": file_data_response},
        )

        file = await protect_client.application.upload_file(
            file_data=b"GIF89a...",
            filename="new.gif",
            content_type="image/gif",
            file_type=FileType.ANIMATIONS,
        )
        assert file.original_name == "new.gif"

    async def test_application_upload_file_failed(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test uploading a file failure."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/files/animations",
            payload={"data": []},
        )

        with pytest.raises(ValueError, match="Failed to upload file"):
            await protect_client.application.upload_file(
                file_data=b"test", filename="test.gif"
            )

    async def test_application_trigger_alarm_webhook_success(
        self,
        protect_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test triggering alarm webhook successfully."""
        mock_aioresponse.post(
            "https://192.168.1.1/proxy/protect/integration/v1/alarm-manager/webhook/trigger-1",
            status=204,
        )

        result = await protect_client.application.trigger_alarm_webhook("trigger-1")
        assert result is True

    async def test_application_trigger_alarm_webhook_empty_id(
        self,
        protect_client: UniFiProtectClient,
    ) -> None:
        """Test triggering alarm webhook with empty trigger ID."""
        with pytest.raises(ValueError, match="Trigger ID is required"):
            await protect_client.application.trigger_alarm_webhook("")
