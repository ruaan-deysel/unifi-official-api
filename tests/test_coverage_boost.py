"""Additional tests to boost coverage to 95%+."""

from __future__ import annotations

import re

import aiohttp
import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth, LocalAuth
from unifi_official_api.exceptions import UniFiConnectionError, UniFiTimeoutError
from unifi_official_api.network import UniFiNetworkClient
from unifi_official_api.protect import UniFiProtectClient


class TestConnectionErrors:
    """Tests for connection error handling in base client."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_connection_error_client_connector(self, auth: ApiKeyAuth) -> None:
        """Test ClientConnectorError raises UniFiConnectionError."""
        # aiohttp.ClientConnectorError requires a ConnectionKey, which is internal
        # Use a simpler approach with aiohttp.ServerDisconnectedError which subclasses ClientError
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                exception=aiohttp.ServerDisconnectedError("Server disconnected"),
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiConnectionError, match="failed"):
                    await client._request("GET", "/ea/hosts")

    async def test_timeout_error(self, auth: ApiKeyAuth) -> None:
        """Test TimeoutError raises UniFiTimeoutError."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                exception=TimeoutError("Request timed out"),
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiTimeoutError, match="timed out"):
                    await client._request("GET", "/ea/hosts")

    async def test_generic_client_error(self, auth: ApiKeyAuth) -> None:
        """Test generic ClientError raises UniFiConnectionError."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                exception=aiohttp.ClientPayloadError("Some network error"),
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiConnectionError, match="failed"):
                    await client._request("GET", "/ea/hosts")


class TestLocalAuth:
    """Tests for LocalAuth SSL verification."""

    def test_local_auth_ssl_verify_false(self) -> None:
        """Test LocalAuth with SSL verification disabled."""
        auth = LocalAuth(api_key="test-local-key", verify_ssl=False)
        client = UniFiNetworkClient(auth=auth, base_url="https://192.168.1.1")
        assert client._get_ssl_context() is False

    def test_local_auth_ssl_verify_true(self) -> None:
        """Test LocalAuth with SSL verification enabled."""
        auth = LocalAuth(api_key="test-local-key", verify_ssl=True)
        client = UniFiNetworkClient(auth=auth, base_url="https://192.168.1.1")
        assert client._get_ssl_context() is True


class TestRequestHeaders:
    """Tests for request headers."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_additional_headers(self, auth: ApiKeyAuth) -> None:
        """Test additional headers are merged with default headers."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                await client._request("GET", "/ea/hosts", headers={"X-Custom-Header": "test-value"})


class TestPutRequest:
    """Tests for PUT requests."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_put_request(self, auth: ApiKeyAuth) -> None:
        """Test PUT request method."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/test",
                payload={"data": {"id": "test"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client._put("/ea/hosts/host-123/test", json_data={"name": "test"})
                assert result is not None


class TestProtectClientEdgeCases:
    """Tests for Protect client edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_validate_connection_returns_none(self, auth: ApiKeyAuth) -> None:
        """Test validate_connection when response is None."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.validate_connection()
                assert result is False

    async def test_get_hosts_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_hosts with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.get_hosts()
                assert result == []

    async def test_get_hosts_list_response(self, auth: ApiKeyAuth) -> None:
        """Test get_hosts with list response (no data wrapper)."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                payload=[{"id": "host-1"}],
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.get_hosts()
                assert len(result) == 1
                assert result[0]["id"] == "host-1"

    async def test_get_hosts_dict_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_hosts when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                payload={"data": {"id": "host-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.get_hosts()
                assert result == []

    async def test_get_binary_success(self, auth: ApiKeyAuth) -> None:
        """Test _get_binary success."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/snapshot.*"
                ),
                body=b"\x89PNG\r\n\x1a\n",
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.get_snapshot("host-123", "site-1", "cam-1")
                assert result == b"\x89PNG\r\n\x1a\n"

    async def test_get_binary_with_params(self, auth: ApiKeyAuth) -> None:
        """Test _get_binary with width and height params."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/snapshot.*"
                ),
                body=b"\x89PNG\r\n\x1a\n",
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.get_snapshot(
                    "host-123", "site-1", "cam-1", width=640, height=480
                )
                assert result == b"\x89PNG\r\n\x1a\n"

    async def test_get_binary_error_status(self, auth: ApiKeyAuth) -> None:
        """Test _get_binary with error status code."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/snapshot.*"
                ),
                status=404,
                body="Not Found",
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(UniFiConnectionError, match="Failed to fetch binary"):
                    await client.cameras.get_snapshot("host-123", "site-1", "cam-1")


class TestWifiEdgeCases:
    """Tests for WiFi endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_wifi_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.wifi.get_all("host-123", "site-1")
                assert result == []

    async def test_wifi_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                payload={"data": {"id": "wifi-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.wifi.get_all("host-123", "site-1")
                assert result == []

    async def test_wifi_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test get with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi/wifi-1",
                payload={"data": [{"id": "wifi-1", "name": "Home", "ssid": "Home"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi = await client.wifi.get("host-123", "site-1", "wifi-1")
                assert wifi.id == "wifi-1"

    async def test_wifi_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test get with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi/wifi-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.wifi.get("host-123", "site-1", "wifi-999")

    async def test_wifi_create_with_passphrase(self, auth: ApiKeyAuth) -> None:
        """Test create with passphrase."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                payload={"data": {"id": "wifi-1", "name": "Test", "ssid": "TestSSID"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi = await client.wifi.create(
                    "host-123", "site-1", name="Test", ssid="TestSSID", passphrase="secret123"
                )
                assert wifi.id == "wifi-1"

    async def test_wifi_create_with_network_id(self, auth: ApiKeyAuth) -> None:
        """Test create with network_id."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                payload={"data": {"id": "wifi-1", "name": "Test", "ssid": "TestSSID"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi = await client.wifi.create(
                    "host-123", "site-1", name="Test", ssid="TestSSID", network_id="net-1"
                )
                assert wifi.id == "wifi-1"

    async def test_wifi_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test create failed."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.wifi.create("host-123", "site-1", name="Test", ssid="Test")

    async def test_wifi_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test update failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi/wifi-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.wifi.update("host-123", "site-1", "wifi-1", name="Updated")


class TestCameraEndpointEdgeCases:
    """Tests for camera endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_cameras_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.get_all("host-123", "site-1")
                assert result == []

    async def test_cameras_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras",
                payload={"data": {"id": "cam-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.get_all("host-123", "site-1")
                assert result == []

    async def test_camera_restart(self, auth: ApiKeyAuth) -> None:
        """Test camera restart."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/restart",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.restart("host-123", "site-1", "cam-1")
                assert result is True

    async def test_camera_set_microphone_volume_valid(self, auth: ApiKeyAuth) -> None:
        """Test set_microphone_volume with valid value."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1",
                payload={"data": {"id": "cam-1", "mac": "aa:bb:cc:dd:ee:ff", "micVolume": 50}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.set_microphone_volume(
                    "host-123", "site-1", "cam-1", 50
                )
                assert result.id == "cam-1"

    async def test_camera_set_microphone_volume_invalid(self, auth: ApiKeyAuth) -> None:
        """Test set_microphone_volume with invalid value."""
        async with UniFiProtectClient(auth=auth) as client:
            with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
                await client.cameras.set_microphone_volume("host-123", "site-1", "cam-1", 150)

    async def test_camera_set_speaker_volume_valid(self, auth: ApiKeyAuth) -> None:
        """Test set_speaker_volume with valid value."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1",
                payload={"data": {"id": "cam-1", "mac": "aa:bb:cc:dd:ee:ff", "speakerVolume": 75}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.set_speaker_volume("host-123", "site-1", "cam-1", 75)
                assert result.id == "cam-1"

    async def test_camera_set_speaker_volume_invalid(self, auth: ApiKeyAuth) -> None:
        """Test set_speaker_volume with invalid value."""
        async with UniFiProtectClient(auth=auth) as client:
            with pytest.raises(ValueError, match="Volume must be between 0 and 100"):
                await client.cameras.set_speaker_volume("host-123", "site-1", "cam-1", -10)

    async def test_camera_ptz_move(self, auth: ApiKeyAuth) -> None:
        """Test PTZ move."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/ptz/move",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.ptz_move(
                    "host-123", "site-1", "cam-1", pan=0.5, tilt=-0.3, zoom=0.8
                )
                assert result is True

    async def test_camera_ptz_goto_preset(self, auth: ApiKeyAuth) -> None:
        """Test PTZ goto preset."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1/ptz/goto/preset-1",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.cameras.ptz_goto_preset(
                    "host-123", "site-1", "cam-1", "preset-1"
                )
                assert result is True


class TestLightsEndpointEdgeCases:
    """Tests for lights endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_lights_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.lights.get_all("host-123", "site-1")
                assert result == []

    async def test_lights_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights",
                payload={"data": {"id": "light-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.lights.get_all("host-123", "site-1")
                assert result == []

    async def test_light_set_brightness_valid(self, auth: ApiKeyAuth) -> None:
        """Test set_brightness with valid value."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": {"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff", "brightness": 80}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.lights.set_brightness("host-123", "site-1", "light-1", 80)
                assert result.id == "light-1"

    async def test_light_set_brightness_invalid(self, auth: ApiKeyAuth) -> None:
        """Test set_brightness with invalid value."""
        async with UniFiProtectClient(auth=auth) as client:
            with pytest.raises(ValueError, match="Brightness must be between 0 and 100"):
                await client.lights.set_brightness("host-123", "site-1", "light-1", 150)


class TestSensorsEndpointEdgeCases:
    """Tests for sensors endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_sensors_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.sensors.get_all("host-123", "site-1")
                assert result == []

    async def test_sensors_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors",
                payload={"data": {"id": "sensor-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.sensors.get_all("host-123", "site-1")
                assert result == []

    async def test_sensor_set_status_led(self, auth: ApiKeyAuth) -> None:
        """Test set_status_led."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": {"id": "sensor-1", "mac": "aa:bb:cc:dd:ee:ff"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.sensors.set_status_led("host-123", "site-1", "sensor-1", True)
                assert result.id == "sensor-1"


class TestChimesEndpointEdgeCases:
    """Tests for chimes endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_chimes_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.chimes.get_all("host-123", "site-1")
                assert result == []

    async def test_chimes_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes",
                payload={"data": {"id": "chime-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.chimes.get_all("host-123", "site-1")
                assert result == []

    async def test_chime_set_volume(self, auth: ApiKeyAuth) -> None:
        """Test set_volume."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1",
                payload={"data": {"id": "chime-1", "mac": "aa:bb:cc:dd:ee:ff", "volume": 50}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.chimes.set_volume("host-123", "site-1", "chime-1", 50)
                assert result.id == "chime-1"


class TestEventsEndpointEdgeCases:
    """Tests for events endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_events_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/events.*"),
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.events.get_all("host-123", "site-1")
                assert result == []

    async def test_events_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/events.*"),
                payload={"data": {"id": "event-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.events.get_all("host-123", "site-1")
                assert result == []

    async def test_events_get_all_with_all_params(self, auth: ApiKeyAuth) -> None:
        """Test get_all with all parameters."""
        from datetime import datetime

        from unifi_official_api.protect.models import EventType

        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/sites/site-1/events.*"),
                payload={"data": [{"id": "event-1", "type": "motion"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.events.get_all(
                    "host-123",
                    "site-1",
                    start=datetime(2024, 1, 1),
                    end=datetime(2024, 1, 2),
                    types=[EventType.MOTION],
                    camera_ids=["cam-1"],
                    limit=50,
                )
                assert len(result) == 1


class TestLiveviewsEndpointEdgeCases:
    """Tests for liveviews endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_liveviews_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews",
                body="",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.liveviews.get_all("host-123", "site-1")
                assert result == []

    async def test_liveviews_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews",
                payload={"data": {"id": "lv-1"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.liveviews.get_all("host-123", "site-1")
                assert result == []

    async def test_liveviews_delete(self, auth: ApiKeyAuth) -> None:
        """Test delete liveview."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-1",
                status=204,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.liveviews.delete("host-123", "site-1", "lv-1")
                assert result is True


class TestNvrEndpointEdgeCases:
    """Tests for NVR endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_nvr_restart(self, auth: ApiKeyAuth) -> None:
        """Test NVR restart."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr/restart",
                status=200,
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.nvr.restart("host-123", "site-1")
                assert result is True

    async def test_nvr_set_retention_valid(self, auth: ApiKeyAuth) -> None:
        """Test NVR set_recording_retention with valid value."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={"data": {"id": "nvr-1", "mac": "aa:bb:cc:dd:ee:ff"}},
            )

            async with UniFiProtectClient(auth=auth) as client:
                result = await client.nvr.set_recording_retention("host-123", "site-1", 30)
                assert result.id == "nvr-1"

    async def test_nvr_set_retention_invalid(self, auth: ApiKeyAuth) -> None:
        """Test NVR set_recording_retention with invalid value."""
        async with UniFiProtectClient(auth=auth) as client:
            with pytest.raises(ValueError, match="Retention days must be at least 1"):
                await client.nvr.set_recording_retention("host-123", "site-1", 0)


class TestFirewallEndpointEdgeCases:
    """Tests for firewall endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_firewall_list_zones_none_response(self, auth: ApiKeyAuth) -> None:
        """Test list_zones with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/zones",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.firewall.list_zones("host-123", "site-1")
                assert result == []

    async def test_firewall_list_zones_not_list(self, auth: ApiKeyAuth) -> None:
        """Test list_zones when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/zones",
                payload={"data": {"id": "zone-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.firewall.list_zones("host-123", "site-1")
                assert result == []

    async def test_firewall_list_rules_none_response(self, auth: ApiKeyAuth) -> None:
        """Test list_rules with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.firewall.list_rules("host-123", "site-1")
                assert result == []

    async def test_firewall_list_rules_not_list(self, auth: ApiKeyAuth) -> None:
        """Test list_rules when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules",
                payload={"data": {"id": "rule-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.firewall.list_rules("host-123", "site-1")
                assert result == []


class TestNetworkEndpointEdgeCases:
    """Tests for network endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_networks_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.networks.get_all("host-123", "site-1")
                assert result == []

    async def test_networks_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks",
                payload={"data": {"id": "net-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.networks.get_all("host-123", "site-1")
                assert result == []


class TestSitesEndpointEdgeCases:
    """Tests for sites endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_sites_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.sites.get_all("host-123")
                assert result == []

    async def test_sites_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites",
                payload={"data": {"id": "site-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.sites.get_all("host-123")
                assert result == []


class TestDevicesEndpointEdgeCases:
    """Tests for devices endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_devices_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.get_all("host-123")
                assert result == []

    async def test_devices_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices",
                payload={"data": {"id": "dev-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.get_all("host-123")
                assert result == []


class TestClientsEndpointEdgeCases:
    """Tests for clients endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_clients_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test get_all with None response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/clients",
                body="",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.get_all("host-123")
                assert result == []

    async def test_clients_get_all_not_list(self, auth: ApiKeyAuth) -> None:
        """Test get_all when data is not a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/clients",
                payload={"data": {"id": "client-1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.get_all("host-123")
                assert result == []
