"""Tests for edge cases and additional coverage."""

from __future__ import annotations

import re

import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth
from unifi_official_api.network import UniFiNetworkClient
from unifi_official_api.protect import UniFiProtectClient


class TestNetworkEndpointEdgeCases:
    """Tests for network endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_sites_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing sites with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                sites = await client.sites.get_all("host-123")
                assert sites == []

    async def test_sites_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting site with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1",
                payload={"data": [{"id": "site-1", "name": "Default"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                site = await client.sites.get("host-123", "site-1")
                assert site.id == "site-1"

    async def test_sites_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting site not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.sites.get("host-123", "site-999")

    async def test_devices_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting device with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-1",
                payload={"data": [{"id": "dev-1", "mac": "aa:bb:cc:dd:ee:ff", "model": "USW"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                device = await client.devices.get("host-123", "dev-1")
                assert device.id == "dev-1"

    async def test_devices_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting device not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.devices.get("host-123", "dev-999")

    async def test_clients_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting client with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/clients/client-1",
                payload={"data": [{"id": "client-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                client_info = await client.clients.get("host-123", "client-1")
                assert client_info.id == "client-1"

    async def test_clients_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting client not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/clients/client-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.clients.get("host-123", "client-999")

    async def test_clients_get_all_with_site(self, auth: ApiKeyAuth) -> None:
        """Test listing clients filtered by site."""
        with aioresponses() as m:
            m.get(
                re.compile(r"https://api\.ui\.com/ea/hosts/host-123/clients.*"),
                payload={"data": [{"id": "client-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                clients = await client.clients.get_all("host-123", site_id="site-1")
                assert len(clients) == 1

    async def test_networks_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting network with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks/net-1",
                payload={"data": [{"id": "net-1", "name": "LAN"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                network = await client.networks.get("host-123", "site-1", "net-1")
                assert network.id == "net-1"

    async def test_networks_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting network not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks/net-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.networks.get("host-123", "site-1", "net-999")

    async def test_networks_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating network failed - returns list instead of dict."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.networks.create("host-123", "site-1", name="Test")

    async def test_networks_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating network failed - returns list instead of dict."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks/net-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.networks.update("host-123", "site-1", "net-1", name="Test")

    async def test_wifi_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific WiFi network."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi/wifi-1",
                payload={"data": {"id": "wifi-1", "name": "Home", "ssid": "Home"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi = await client.wifi.get("host-123", "site-1", "wifi-1")
                assert wifi.id == "wifi-1"

    async def test_wifi_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a WiFi network."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi/wifi-1",
                payload={"data": {"id": "wifi-1", "name": "Updated", "ssid": "Updated"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi = await client.wifi.update("host-123", "site-1", "wifi-1", name="Updated")
                assert wifi.name == "Updated"

    async def test_wifi_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a WiFi network."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi/wifi-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.wifi.delete("host-123", "site-1", "wifi-1")
                assert result is True

    async def test_firewall_get_rule_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting firewall rule with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules/rule-1",
                payload={"data": [{"id": "rule-1", "name": "Block"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.firewall.get_rule("host-123", "site-1", "rule-1")
                assert rule.id == "rule-1"

    async def test_firewall_get_rule_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting firewall rule not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules/rule-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.firewall.get_rule("host-123", "site-1", "rule-999")

    async def test_firewall_create_rule_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating firewall rule failed."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.firewall.create_rule("host-123", "site-1", name="Test")

    async def test_firewall_update_rule_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating firewall rule failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules/rule-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.firewall.update_rule("host-123", "site-1", "rule-1", name="Test")


class TestProtectEndpointEdgeCases:
    """Tests for protect endpoint edge cases."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_cameras_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting camera with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1",
                payload={"data": [{"id": "cam-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                camera = await client.cameras.get("host-123", "site-1", "cam-1")
                assert camera.id == "cam-1"

    async def test_cameras_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting camera not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-999",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.cameras.get("host-123", "site-1", "cam-999")

    async def test_cameras_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating camera failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/cameras/cam-1",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.cameras.update("host-123", "site-1", "cam-1", name="Test")

    async def test_sensors_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting sensor with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": [{"id": "sensor-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                sensor = await client.sensors.get("host-123", "site-1", "sensor-1")
                assert sensor.id == "sensor-1"

    async def test_sensors_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting sensor not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-999",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.sensors.get("host-123", "site-1", "sensor-999")

    async def test_sensors_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating sensor failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/sensors/sensor-1",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.sensors.update("host-123", "site-1", "sensor-1", name="Test")

    async def test_lights_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting light with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": [{"id": "light-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                light = await client.lights.get("host-123", "site-1", "light-1")
                assert light.id == "light-1"

    async def test_lights_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting light not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-999",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.lights.get("host-123", "site-1", "light-999")

    async def test_lights_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating light failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/lights/light-1",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.lights.update("host-123", "site-1", "light-1", name="Test")

    async def test_chimes_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting chime with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1",
                payload={"data": [{"id": "chime-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                chime = await client.chimes.get("host-123", "site-1", "chime-1")
                assert chime.id == "chime-1"

    async def test_chimes_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting chime not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-999",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.chimes.get("host-123", "site-1", "chime-999")

    async def test_chimes_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating chime failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/chimes/chime-1",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.chimes.update("host-123", "site-1", "chime-1", name="Test")

    async def test_nvr_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting NVR with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={"data": [{"id": "nvr-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                nvr = await client.nvr.get("host-123", "site-1")
                assert nvr.id == "nvr-1"

    async def test_nvr_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting NVR not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.nvr.get("host-123", "site-1")

    async def test_nvr_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating NVR failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/nvr",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.nvr.update("host-123", "site-1", name="Test")

    async def test_liveviews_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting live view with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-1",
                payload={"data": [{"id": "lv-1", "name": "Main"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                liveview = await client.liveviews.get("host-123", "site-1", "lv-1")
                assert liveview.id == "lv-1"

    async def test_liveviews_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting live view not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-999",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.liveviews.get("host-123", "site-1", "lv-999")

    async def test_liveviews_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating live view failed."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.liveviews.create("host-123", "site-1", name="Test")

    async def test_liveviews_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating live view failed."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/liveviews/lv-1",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.liveviews.update("host-123", "site-1", "lv-1", name="Test")

    async def test_events_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting event with list response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/events/event-1",
                payload={"data": [{"id": "event-1", "type": "motion"}]},
            )

            async with UniFiProtectClient(auth=auth) as client:
                event = await client.events.get("host-123", "site-1", "event-1")
                assert event.id == "event-1"

    async def test_events_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting event not found."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/events/event-999",
                payload={"data": []},
            )

            async with UniFiProtectClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.events.get("host-123", "site-1", "event-999")


class TestModelDisplayNames:
    """Tests for model display_name properties."""

    def test_chime_display_name(self) -> None:
        """Test chime display_name property."""
        from unifi_official_api.protect import Chime

        chime = Chime.model_validate({"id": "1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Doorbell"})
        assert chime.display_name == "Doorbell"

        chime = Chime.model_validate({"id": "2", "mac": "aa:bb:cc:dd:ee:ff"})
        assert chime.display_name == "aa:bb:cc:dd:ee:ff"

    def test_light_display_name(self) -> None:
        """Test light display_name property."""
        from unifi_official_api.protect import Light

        light = Light.model_validate({"id": "1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Floodlight"})
        assert light.display_name == "Floodlight"

        light = Light.model_validate({"id": "2", "mac": "aa:bb:cc:dd:ee:ff"})
        assert light.display_name == "aa:bb:cc:dd:ee:ff"

    def test_sensor_display_name(self) -> None:
        """Test sensor display_name property."""
        from unifi_official_api.protect import Sensor

        sensor = Sensor.model_validate({"id": "1", "mac": "aa:bb:cc:dd:ee:ff", "name": "Door"})
        assert sensor.display_name == "Door"

        sensor = Sensor.model_validate({"id": "2", "mac": "aa:bb:cc:dd:ee:ff"})
        assert sensor.display_name == "aa:bb:cc:dd:ee:ff"

    def test_nvr_display_name(self) -> None:
        """Test NVR display_name property."""
        from unifi_official_api.protect import NVR

        nvr = NVR.model_validate({"id": "1", "mac": "aa:bb:cc:dd:ee:ff", "name": "My NVR"})
        assert nvr.display_name == "My NVR"

        nvr = NVR.model_validate({"id": "2", "mac": "aa:bb:cc:dd:ee:ff"})
        assert nvr.display_name == "aa:bb:cc:dd:ee:ff"

    def test_nvr_storage_usage(self) -> None:
        """Test NVR storage usage calculation."""
        from unifi_official_api.protect.models.nvr import StorageInfo

        storage = StorageInfo.model_validate({"totalSize": 1000, "usedSize": 250})
        assert storage.usage_percent == 25.0

        storage = StorageInfo.model_validate({"totalSize": 0, "usedSize": 0})
        assert storage.usage_percent == 0.0
