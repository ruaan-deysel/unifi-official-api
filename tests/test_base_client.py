"""Tests for base client functionality."""

from __future__ import annotations

import pytest
from aioresponses import aioresponses

from unifi_official_api import (
    ApiKeyAuth,
    UniFiAuthenticationError,
    UniFiNotFoundError,
    UniFiRateLimitError,
    UniFiResponseError,
)
from unifi_official_api.network import UniFiNetworkClient


class TestBaseClientErrorHandling:
    """Tests for base client error handling."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_authentication_error_401(self, auth: ApiKeyAuth) -> None:
        """Test 401 unauthorized raises authentication error."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=401,
                body="Unauthorized",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiAuthenticationError) as exc_info:
                    await client.get_hosts()
                assert "Authentication failed" in str(exc_info.value)

    async def test_authentication_error_403(self, auth: ApiKeyAuth) -> None:
        """Test 403 forbidden raises authentication error."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=403,
                body="Forbidden",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiAuthenticationError) as exc_info:
                    await client.get_hosts()
                assert "Access forbidden" in str(exc_info.value)

    async def test_not_found_error(self, auth: ApiKeyAuth) -> None:
        """Test 404 not found raises not found error."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/device-999",
                status=404,
                body="Not Found",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiNotFoundError) as exc_info:
                    await client.devices.get("host-123", "device-999")
                assert exc_info.value.status_code == 404

    async def test_rate_limit_error(self, auth: ApiKeyAuth) -> None:
        """Test 429 rate limit raises rate limit error."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=429,
                body="Too Many Requests",
                headers={"Retry-After": "30"},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiRateLimitError) as exc_info:
                    await client.get_hosts()
                assert exc_info.value.retry_after == 30

    async def test_rate_limit_error_no_retry_header(self, auth: ApiKeyAuth) -> None:
        """Test 429 rate limit without Retry-After header."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=429,
                body="Too Many Requests",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiRateLimitError) as exc_info:
                    await client.get_hosts()
                assert exc_info.value.retry_after == 60  # Default

    async def test_server_error(self, auth: ApiKeyAuth) -> None:
        """Test 500 server error raises response error."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=500,
                body="Internal Server Error",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(UniFiResponseError) as exc_info:
                    await client.get_hosts()
                assert exc_info.value.status_code == 500

    async def test_empty_response(self, auth: ApiKeyAuth) -> None:
        """Test handling of empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=200,
                body="",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.get_hosts()
                assert result == []

    async def test_non_json_response(self, auth: ApiKeyAuth) -> None:
        """Test handling of non-JSON response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts",
                status=200,
                body="Not JSON content",
                content_type="text/plain",
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.get_hosts()
                assert result == []


class TestNetworkEndpoints:
    """Tests for network endpoint methods."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_sites_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing sites."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites",
                payload={"data": [{"id": "site-1", "name": "Default"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                sites = await client.sites.get_all("host-123")
                assert len(sites) == 1
                assert sites[0].id == "site-1"

    async def test_sites_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific site."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1",
                payload={"data": {"id": "site-1", "name": "Default"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                site = await client.sites.get("host-123", "site-1")
                assert site.id == "site-1"

    async def test_networks_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing networks."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks",
                payload={"data": [{"id": "net-1", "name": "LAN", "vlan": 1}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                networks = await client.networks.get_all("host-123", "site-1")
                assert len(networks) == 1
                assert networks[0].id == "net-1"

    async def test_networks_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific network."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks/net-1",
                payload={"data": {"id": "net-1", "name": "LAN"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                network = await client.networks.get("host-123", "site-1", "net-1")
                assert network.id == "net-1"

    async def test_networks_create(self, auth: ApiKeyAuth) -> None:
        """Test creating a network."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks",
                payload={"data": {"id": "net-2", "name": "Guest", "vlan": 10}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                network = await client.networks.create(
                    "host-123", "site-1", name="Guest", vlan=10
                )
                assert network.id == "net-2"

    async def test_networks_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a network."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks/net-1",
                payload={"data": {"id": "net-1", "name": "Updated"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                network = await client.networks.update(
                    "host-123", "site-1", "net-1", name="Updated"
                )
                assert network.name == "Updated"

    async def test_networks_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a network."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/networks/net-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.networks.delete("host-123", "site-1", "net-1")
                assert result is True

    async def test_wifi_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing WiFi networks."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                payload={"data": [{"id": "wifi-1", "name": "Home WiFi", "ssid": "Home"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi_networks = await client.wifi.get_all("host-123", "site-1")
                assert len(wifi_networks) == 1
                assert wifi_networks[0].ssid == "Home"

    async def test_wifi_create(self, auth: ApiKeyAuth) -> None:
        """Test creating a WiFi network."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/wifi",
                payload={"data": {"id": "wifi-2", "name": "Guest WiFi", "ssid": "Guest"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                wifi = await client.wifi.create(
                    "host-123", "site-1", name="Guest WiFi", ssid="Guest"
                )
                assert wifi.ssid == "Guest"

    async def test_firewall_list_zones(self, auth: ApiKeyAuth) -> None:
        """Test listing firewall zones."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/zones",
                payload={"data": [{"id": "zone-1", "name": "LAN"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                zones = await client.firewall.list_zones("host-123", "site-1")
                assert len(zones) == 1
                assert zones[0].name == "LAN"

    async def test_firewall_list_rules(self, auth: ApiKeyAuth) -> None:
        """Test listing firewall rules."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules",
                payload={"data": [{"id": "rule-1", "name": "Block", "action": "drop"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rules = await client.firewall.list_rules("host-123", "site-1")
                assert len(rules) == 1
                assert rules[0].name == "Block"

    async def test_firewall_get_rule(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific firewall rule."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules/rule-1",
                payload={"data": {"id": "rule-1", "name": "Block"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.firewall.get_rule("host-123", "site-1", "rule-1")
                assert rule.id == "rule-1"

    async def test_firewall_create_rule(self, auth: ApiKeyAuth) -> None:
        """Test creating a firewall rule."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules",
                payload={"data": {"id": "rule-2", "name": "New Rule", "action": "accept"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.firewall.create_rule(
                    "host-123", "site-1", name="New Rule", action="accept"
                )
                assert rule.name == "New Rule"

    async def test_firewall_update_rule(self, auth: ApiKeyAuth) -> None:
        """Test updating a firewall rule."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules/rule-1",
                payload={"data": {"id": "rule-1", "name": "Updated Rule"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.firewall.update_rule(
                    "host-123", "site-1", "rule-1", name="Updated Rule"
                )
                assert rule.name == "Updated Rule"

    async def test_firewall_delete_rule(self, auth: ApiKeyAuth) -> None:
        """Test deleting a firewall rule."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/firewall/rules/rule-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.firewall.delete_rule("host-123", "site-1", "rule-1")
                assert result is True

    async def test_clients_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific client."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/clients/client-1",
                payload={"data": {"id": "client-1", "mac": "aa:bb:cc:dd:ee:ff"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                client_info = await client.clients.get("host-123", "client-1")
                assert client_info.id == "client-1"

    async def test_clients_block(self, auth: ApiKeyAuth) -> None:
        """Test blocking a client."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/clients/aa:bb:cc:dd:ee:ff/block",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.block("host-123", "site-1", "aa:bb:cc:dd:ee:ff")
                assert result is True

    async def test_clients_unblock(self, auth: ApiKeyAuth) -> None:
        """Test unblocking a client."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/clients/aa:bb:cc:dd:ee:ff/unblock",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.unblock("host-123", "site-1", "aa:bb:cc:dd:ee:ff")
                assert result is True

    async def test_clients_reconnect(self, auth: ApiKeyAuth) -> None:
        """Test reconnecting a client."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/clients/aa:bb:cc:dd:ee:ff/reconnect",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.reconnect("host-123", "site-1", "aa:bb:cc:dd:ee:ff")
                assert result is True

    async def test_devices_restart(self, auth: ApiKeyAuth) -> None:
        """Test restarting a device."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/devices/device-1/restart",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.restart("host-123", "device-1")
                assert result is True

    async def test_devices_adopt(self, auth: ApiKeyAuth) -> None:
        """Test adopting a device."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/devices/adopt",
                status=200,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.adopt("host-123", "site-1", "aa:bb:cc:dd:ee:ff")
                assert result is True

    async def test_devices_forget(self, auth: ApiKeyAuth) -> None:
        """Test forgetting a device."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/devices/device-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.forget("host-123", "device-1")
                assert result is True
