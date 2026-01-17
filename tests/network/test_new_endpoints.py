"""Tests for new Network API endpoints (vouchers, ACL, traffic, resources)."""

from __future__ import annotations

import re

import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth
from unifi_official_api.network import UniFiNetworkClient
from unifi_official_api.network.models import ACLAction, ACLRuleType, TrafficMatchingType
from unifi_official_api.protect import UniFiProtectClient


class TestVouchersEndpoint:
    """Tests for vouchers endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_vouchers_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing vouchers."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/hotspot/vouchers.*"),
                payload={
                    "data": [
                        {"id": "v-1", "code": "1234567890", "expired": False},
                        {"id": "v-2", "code": "0987654321", "expired": True},
                    ]
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                vouchers = await client.vouchers.get_all("host-123", "site-1")
                assert len(vouchers) == 2
                assert vouchers[0].code == "1234567890"
                assert vouchers[1].expired is True

    async def test_vouchers_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing vouchers with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/hotspot/vouchers.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                vouchers = await client.vouchers.get_all("host-123", "site-1")
                assert vouchers == []

    async def test_vouchers_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific voucher."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers/v-1",
                payload={"data": {"id": "v-1", "code": "1234567890", "expired": False}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                voucher = await client.vouchers.get("host-123", "site-1", "v-1")
                assert voucher.id == "v-1"
                assert voucher.code == "1234567890"

    async def test_vouchers_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting a voucher that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers/v-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.vouchers.get("host-123", "site-1", "v-999")

    async def test_vouchers_create(self, auth: ApiKeyAuth) -> None:
        """Test creating vouchers."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers",
                payload={
                    "data": [
                        {"id": "v-1", "code": "1111111111", "expired": False},
                        {"id": "v-2", "code": "2222222222", "expired": False},
                    ]
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                vouchers = await client.vouchers.create(
                    "host-123",
                    "site-1",
                    count=2,
                    name="Test Voucher",
                    time_limit_minutes=1440,
                )
                assert len(vouchers) == 2

    async def test_vouchers_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating vouchers failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.vouchers.create("host-123", "site-1", count=1)

    async def test_vouchers_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a voucher."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers/v-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.vouchers.delete("host-123", "site-1", "v-1")
                assert result is True

    async def test_vouchers_delete_multiple(self, auth: ApiKeyAuth) -> None:
        """Test deleting multiple vouchers."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers/v-1",
                status=204,
            )
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers/v-2",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.vouchers.delete_multiple("host-123", "site-1", ["v-1", "v-2"])
                assert result is True


class TestACLEndpoint:
    """Tests for ACL endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_acl_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing ACL rules."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/acl-rules.*"),
                payload={
                    "data": [
                        {
                            "id": "acl-1",
                            "type": "IPV4",
                            "name": "Block Rule",
                            "action": "BLOCK",
                            "enabled": True,
                            "index": 0,
                        }
                    ]
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rules = await client.acl.get_all("host-123", "site-1")
                assert len(rules) == 1
                assert rules[0].name == "Block Rule"
                assert rules[0].action == ACLAction.BLOCK

    async def test_acl_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing ACL rules with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/acl-rules.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rules = await client.acl.get_all("host-123", "site-1")
                assert rules == []

    async def test_acl_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific ACL rule."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules/acl-1",
                payload={
                    "data": {
                        "id": "acl-1",
                        "type": "IPV4",
                        "name": "Block Rule",
                        "action": "BLOCK",
                        "enabled": True,
                        "index": 0,
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.acl.get("host-123", "site-1", "acl-1")
                assert rule.id == "acl-1"

    async def test_acl_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting an ACL rule that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules/acl-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.acl.get("host-123", "site-1", "acl-999")

    async def test_acl_create(self, auth: ApiKeyAuth) -> None:
        """Test creating an ACL rule."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules",
                payload={
                    "data": {
                        "id": "acl-new",
                        "type": "IPV4",
                        "name": "New Rule",
                        "action": "ALLOW",
                        "enabled": True,
                        "index": 0,
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.acl.create(
                    "host-123",
                    "site-1",
                    name="New Rule",
                    rule_type=ACLRuleType.IPV4,
                    action=ACLAction.ALLOW,
                    index=0,
                )
                assert rule.id == "acl-new"

    async def test_acl_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating an ACL rule failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.acl.create("host-123", "site-1", name="Test", index=0)

    async def test_acl_update(self, auth: ApiKeyAuth) -> None:
        """Test updating an ACL rule."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules/acl-1",
                payload={
                    "data": {
                        "id": "acl-1",
                        "type": "IPV4",
                        "name": "Updated Rule",
                        "action": "BLOCK",
                        "enabled": True,
                        "index": 0,
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.acl.update("host-123", "site-1", "acl-1", name="Updated Rule")
                assert rule.name == "Updated Rule"

    async def test_acl_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating an ACL rule failure."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules/acl-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.acl.update("host-123", "site-1", "acl-1", name="Test")

    async def test_acl_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting an ACL rule."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules/acl-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.acl.delete("host-123", "site-1", "acl-1")
                assert result is True


class TestTrafficEndpoint:
    """Tests for traffic endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_traffic_get_all_lists(self, auth: ApiKeyAuth) -> None:
        """Test listing traffic matching lists."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/traffic-matching-lists.*"),
                payload={
                    "data": [
                        {"id": "list-1", "type": "IP_ADDRESS", "name": "Block List", "entries": []}
                    ]
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                lists = await client.traffic.get_all_lists("host-123", "site-1")
                assert len(lists) == 1
                assert lists[0].name == "Block List"

    async def test_traffic_get_all_lists_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing traffic matching lists with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/traffic-matching-lists.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                lists = await client.traffic.get_all_lists("host-123", "site-1")
                assert lists == []

    async def test_traffic_get_list(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific traffic matching list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists/list-1",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Block List",
                        "entries": ["1.2.3.4"],
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                traffic_list = await client.traffic.get_list("host-123", "site-1", "list-1")
                assert traffic_list.id == "list-1"
                assert traffic_list.entries == ["1.2.3.4"]

    async def test_traffic_get_list_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting a traffic matching list that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists/l-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.traffic.get_list("host-123", "site-1", "l-999")

    async def test_traffic_create_list(self, auth: ApiKeyAuth) -> None:
        """Test creating a traffic matching list."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists",
                payload={
                    "data": {
                        "id": "list-new",
                        "type": "IP_ADDRESS",
                        "name": "New List",
                        "entries": [],
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                traffic_list = await client.traffic.create_list(
                    "host-123",
                    "site-1",
                    name="New List",
                    list_type=TrafficMatchingType.IP_ADDRESS,
                )
                assert traffic_list.id == "list-new"

    async def test_traffic_create_list_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating a traffic matching list failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.traffic.create_list(
                        "host-123", "site-1", name="Test", list_type=TrafficMatchingType.IP_ADDRESS
                    )

    async def test_traffic_update_list(self, auth: ApiKeyAuth) -> None:
        """Test updating a traffic matching list."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists/list-1",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Updated List",
                        "entries": [],
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                traffic_list = await client.traffic.update_list(
                    "host-123", "site-1", "list-1", name="Updated List"
                )
                assert traffic_list.name == "Updated List"

    async def test_traffic_update_list_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating a traffic matching list failure."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists/list-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.traffic.update_list("host-123", "site-1", "list-1", name="Test")

    async def test_traffic_delete_list(self, auth: ApiKeyAuth) -> None:
        """Test deleting a traffic matching list."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists/list-1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.traffic.delete_list("host-123", "site-1", "list-1")
                assert result is True

    async def test_traffic_get_dpi_categories(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI categories."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/dpi/categories",
                payload={"data": [{"id": "cat-1", "name": "Streaming"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                categories = await client.traffic.get_dpi_categories("host-123", "site-1")
                assert len(categories) == 1
                assert categories[0].name == "Streaming"

    async def test_traffic_get_dpi_categories_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI categories with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/dpi/categories",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                categories = await client.traffic.get_dpi_categories("host-123", "site-1")
                assert categories == []

    async def test_traffic_get_dpi_applications(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI applications."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/dpi/applications",
                payload={"data": [{"id": "app-1", "name": "Netflix"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                apps = await client.traffic.get_dpi_applications("host-123", "site-1")
                assert len(apps) == 1
                assert apps[0].name == "Netflix"

    async def test_traffic_get_dpi_applications_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI applications with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/dpi/applications",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                apps = await client.traffic.get_dpi_applications("host-123", "site-1")
                assert apps == []

    async def test_traffic_get_countries(self, auth: ApiKeyAuth) -> None:
        """Test getting countries."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/geo/countries",
                payload={"data": [{"code": "US", "name": "United States"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                countries = await client.traffic.get_countries("host-123", "site-1")
                assert len(countries) == 1
                assert countries[0].code == "US"

    async def test_traffic_get_countries_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting countries with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/geo/countries",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                countries = await client.traffic.get_countries("host-123", "site-1")
                assert countries == []


class TestResourcesEndpoint:
    """Tests for resources endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_resources_get_wan_interfaces(self, auth: ApiKeyAuth) -> None:
        """Test getting WAN interfaces."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/wan.*"),
                payload={
                    "data": [{"id": "wan-1", "name": "WAN1", "status": "UP", "isPrimary": True}]
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                interfaces = await client.resources.get_wan_interfaces("host-123", "site-1")
                assert len(interfaces) == 1
                assert interfaces[0].name == "WAN1"
                assert interfaces[0].is_primary is True

    async def test_resources_get_wan_interfaces_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting WAN interfaces with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/wan.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                interfaces = await client.resources.get_wan_interfaces("host-123", "site-1")
                assert interfaces == []

    async def test_resources_get_vpn_tunnels(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN tunnels."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/vpn/tunnels.*"),
                payload={"data": [{"id": "vpn-1", "name": "Site-to-Site VPN", "status": "UP"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                tunnels = await client.resources.get_vpn_tunnels("host-123", "site-1")
                assert len(tunnels) == 1
                assert tunnels[0].name == "Site-to-Site VPN"

    async def test_resources_get_vpn_tunnels_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN tunnels with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/vpn/tunnels.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                tunnels = await client.resources.get_vpn_tunnels("host-123", "site-1")
                assert tunnels == []

    async def test_resources_get_vpn_servers(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN servers."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/vpn/servers.*"),
                payload={
                    "data": [
                        {"id": "srv-1", "name": "WireGuard", "type": "WIREGUARD", "enabled": True}
                    ]
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                servers = await client.resources.get_vpn_servers("host-123", "site-1")
                assert len(servers) == 1
                assert servers[0].name == "WireGuard"

    async def test_resources_get_vpn_servers_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN servers with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/vpn/servers.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                servers = await client.resources.get_vpn_servers("host-123", "site-1")
                assert servers == []

    async def test_resources_get_radius_profiles(self, auth: ApiKeyAuth) -> None:
        """Test getting RADIUS profiles."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/radius/profiles.*"),
                payload={"data": [{"id": "rad-1", "name": "Corp RADIUS", "authPort": 1812}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                profiles = await client.resources.get_radius_profiles("host-123", "site-1")
                assert len(profiles) == 1
                assert profiles[0].name == "Corp RADIUS"

    async def test_resources_get_radius_profiles_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting RADIUS profiles with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/radius/profiles.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                profiles = await client.resources.get_radius_profiles("host-123", "site-1")
                assert profiles == []

    async def test_resources_get_device_tags(self, auth: ApiKeyAuth) -> None:
        """Test getting device tags."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/device-tags.*"),
                payload={"data": [{"id": "tag-1", "name": "Production", "deviceCount": 5}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                tags = await client.resources.get_device_tags("host-123", "site-1")
                assert len(tags) == 1
                assert tags[0].name == "Production"
                assert tags[0].device_count == 5

    async def test_resources_get_device_tags_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting device tags with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/device-tags.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                tags = await client.resources.get_device_tags("host-123", "site-1")
                assert tags == []


class TestNetworkClientApplicationInfo:
    """Tests for Network client application info."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_get_application_info(self, auth: ApiKeyAuth) -> None:
        """Test getting application info."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/info",
                payload={"data": {"version": "10.0.162", "name": "UniFi Network"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                info = await client.get_application_info("host-123")
                assert info["version"] == "10.0.162"

    async def test_get_application_info_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting application info with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/info",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                info = await client.get_application_info("host-123")
                assert info == {}


class TestAdditionalCoverage:
    """Additional tests for coverage."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_vouchers_with_filter(self, auth: ApiKeyAuth) -> None:
        """Test listing vouchers with filter query."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/hotspot/vouchers.*"),
                payload={"data": [{"id": "v-1", "code": "123", "expired": False}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                vouchers = await client.vouchers.get_all(
                    "host-123", "site-1", filter_query="active"
                )
                assert len(vouchers) == 1

    async def test_vouchers_with_all_options(self, auth: ApiKeyAuth) -> None:
        """Test creating vouchers with all options."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers",
                payload={"data": [{"id": "v-1", "code": "123", "expired": False}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                vouchers = await client.vouchers.create(
                    "host-123",
                    "site-1",
                    count=1,
                    name="Test",
                    authorized_guest_limit=5,
                    time_limit_minutes=60,
                    data_usage_limit_mbytes=1000,
                    rx_rate_limit_kbps=5000,
                    tx_rate_limit_kbps=2000,
                )
                assert len(vouchers) == 1

    async def test_vouchers_create_single_dict_response(self, auth: ApiKeyAuth) -> None:
        """Test creating voucher with single dict response."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/hotspot/vouchers",
                payload={"data": {"id": "v-1", "code": "123", "expired": False}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                vouchers = await client.vouchers.create("host-123", "site-1", count=1)
                assert len(vouchers) == 1

    async def test_acl_with_filters(self, auth: ApiKeyAuth) -> None:
        """Test ACL with source and destination filters."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules",
                payload={
                    "data": {
                        "id": "acl-1",
                        "type": "IPV4",
                        "name": "Test",
                        "action": "BLOCK",
                        "enabled": True,
                        "index": 0,
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.acl.create(
                    "host-123",
                    "site-1",
                    name="Test",
                    index=0,
                    rule_type=ACLRuleType.IPV4,
                    action=ACLAction.BLOCK,
                    enabled=False,
                    source={"ip_addresses": ["192.168.1.0/24"]},
                    destination={"ip_addresses": ["10.0.0.0/8"]},
                    schedule="always",
                    description="Test rule",
                )
                assert rule.id == "acl-1"

    async def test_traffic_create_list_with_entries(self, auth: ApiKeyAuth) -> None:
        """Test creating traffic list with entries."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Block",
                        "entries": ["1.2.3.4"],
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                lst = await client.traffic.create_list(
                    "host-123",
                    "site-1",
                    name="Block",
                    list_type=TrafficMatchingType.IP_ADDRESS,
                    entries=["1.2.3.4"],
                    description="Block list",
                )
                assert lst.id == "list-1"

    async def test_traffic_update_list_with_entries(self, auth: ApiKeyAuth) -> None:
        """Test updating traffic list with entries."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/traffic-matching-lists/list-1",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Updated",
                        "entries": ["1.2.3.4", "5.6.7.8"],
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                lst = await client.traffic.update_list(
                    "host-123",
                    "site-1",
                    "list-1",
                    name="Updated",
                    entries=["1.2.3.4", "5.6.7.8"],
                )
                assert lst.name == "Updated"

    async def test_acl_update_with_all_options(self, auth: ApiKeyAuth) -> None:
        """Test updating ACL with all options."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/acl-rules/acl-1",
                payload={
                    "data": {
                        "id": "acl-1",
                        "type": "IPV4",
                        "name": "Updated",
                        "action": "ALLOW",
                        "enabled": True,
                        "index": 1,
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rule = await client.acl.update(
                    "host-123",
                    "site-1",
                    "acl-1",
                    name="Updated",
                    action=ACLAction.ALLOW,
                    enabled=True,
                    index=1,
                    source={"ip_addresses": ["0.0.0.0/0"]},
                    destination={"ip_addresses": ["10.0.0.0/8"]},
                    schedule="weekday",
                    description="Updated rule",
                )
                assert rule.name == "Updated"

    async def test_viewers_get_single_dict(self, auth: ApiKeyAuth) -> None:
        """Test viewers get returning dict response instead of list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/viewers",
                payload={
                    "data": {
                        "id": "v-1",
                        "modelKey": "viewer",
                        "state": "CONNECTED",
                        "mac": "aa:bb:cc:dd:ee:ff",
                        "streamLimit": 4,
                    }
                },
            )

            async with UniFiProtectClient(auth=auth) as client:
                viewers = await client.viewers.get_all("host-123", "site-1")
                # Returns empty since not a list
                assert viewers == []


class TestDeviceActions:
    """Tests for device action endpoints."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_device_locate(self, auth: ApiKeyAuth) -> None:
        """Test device locate mode."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-1/locate",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.locate("host-123", "dev-1", enabled=True)
                assert result is True

    async def test_device_get_pending_adoption(self, auth: ApiKeyAuth) -> None:
        """Test getting devices pending adoption."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/pending-adoption",
                payload={"data": [{"id": "dev-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                devices = await client.devices.get_pending_adoption("host-123")
                assert len(devices) == 1

    async def test_device_get_pending_adoption_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting devices pending adoption when empty."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/pending-adoption",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                devices = await client.devices.get_pending_adoption("host-123")
                assert devices == []

    async def test_device_get_statistics(self, auth: ApiKeyAuth) -> None:
        """Test getting device statistics."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-1/statistics/latest",
                payload={"data": {"cpu": 25, "memory": 50}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                stats = await client.devices.get_statistics("host-123", "dev-1")
                assert stats["cpu"] == 25

    async def test_device_get_statistics_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting device statistics when empty."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-1/statistics/latest",
                payload={"data": []},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                stats = await client.devices.get_statistics("host-123", "dev-1")
                assert stats == {}

    async def test_device_port_action(self, auth: ApiKeyAuth) -> None:
        """Test device port action."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-1/ports/1",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.execute_port_action(
                    "host-123", "dev-1", 1, poe_mode="auto", speed="1000", enabled=True
                )
                assert result is True

    async def test_device_port_action_no_settings(self, auth: ApiKeyAuth) -> None:
        """Test device port action without settings raises error."""
        async with UniFiNetworkClient(auth=auth) as client:
            with pytest.raises(ValueError, match="At least one"):
                await client.devices.execute_port_action("host-123", "dev-1", 1)

    async def test_device_execute_action(self, auth: ApiKeyAuth) -> None:
        """Test device execute action."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/devices/dev-1/provision",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.devices.execute_action("host-123", "dev-1", "provision")
                assert result is True

    async def test_device_execute_action_invalid(self, auth: ApiKeyAuth) -> None:
        """Test device execute action with invalid action."""
        async with UniFiNetworkClient(auth=auth) as client:
            with pytest.raises(ValueError, match="Action must be one of"):
                await client.devices.execute_action("host-123", "dev-1", "invalid")


class TestClientActions:
    """Tests for client action endpoints."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_client_forget(self, auth: ApiKeyAuth) -> None:
        """Test client forget."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/clients/aa:bb:cc:dd:ee:ff",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.forget("host-123", "site-1", "aa:bb:cc:dd:ee:ff")
                assert result is True

    async def test_client_execute_action(self, auth: ApiKeyAuth) -> None:
        """Test client execute action."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/clients/aa:bb:cc:dd:ee:ff/block",
                status=204,
            )

            async with UniFiNetworkClient(auth=auth) as client:
                result = await client.clients.execute_action(
                    "host-123", "site-1", "aa:bb:cc:dd:ee:ff", "block"
                )
                assert result is True

    async def test_client_execute_action_invalid(self, auth: ApiKeyAuth) -> None:
        """Test client execute action with invalid action."""
        async with UniFiNetworkClient(auth=auth) as client:
            with pytest.raises(ValueError, match="Action must be one of"):
                await client.clients.execute_action(
                    "host-123", "site-1", "aa:bb:cc:dd:ee:ff", "invalid"
                )


class TestResourcesAdditional:
    """Additional tests for resources endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_wan_interfaces_single_item(self, auth: ApiKeyAuth) -> None:
        """Test WAN interface when data is a single dict."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/wan.*"),
                payload={"data": {"id": "wan-1", "name": "WAN1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                interfaces = await client.resources.get_wan_interfaces("host-123", "site-1")
                # Returns empty since not a list
                assert interfaces == []

    async def test_vpn_tunnels_single_item(self, auth: ApiKeyAuth) -> None:
        """Test VPN tunnels when data is a single dict."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/vpn/tunnels.*"),
                payload={"data": {"id": "vpn-1", "name": "VPN1"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                tunnels = await client.resources.get_vpn_tunnels("host-123", "site-1")
                # Returns empty since not a list
                assert tunnels == []


class TestTrafficAdditional:
    """Additional tests for traffic endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_dpi_categories_single_item(self, auth: ApiKeyAuth) -> None:
        """Test DPI categories when data is a single dict."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/dpi/categories",
                payload={"data": {"id": "cat-1", "name": "Test"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                categories = await client.traffic.get_dpi_categories("host-123", "site-1")
                # Returns empty since not a list
                assert categories == []

    async def test_dpi_applications_single_item(self, auth: ApiKeyAuth) -> None:
        """Test DPI applications when data is a single dict."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/dpi/applications",
                payload={"data": {"id": "app-1", "name": "Test"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                apps = await client.traffic.get_dpi_applications("host-123", "site-1")
                # Returns empty since not a list
                assert apps == []

    async def test_countries_single_item(self, auth: ApiKeyAuth) -> None:
        """Test countries when data is a single dict."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/ea/hosts/host-123/sites/site-1/geo/countries",
                payload={"data": {"code": "US", "name": "USA"}},
            )

            async with UniFiNetworkClient(auth=auth) as client:
                countries = await client.traffic.get_countries("host-123", "site-1")
                # Returns empty since not a list
                assert countries == []

    async def test_traffic_lists_single_item(self, auth: ApiKeyAuth) -> None:
        """Test traffic lists when data is a single dict."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/traffic-matching-lists.*"),
                payload={
                    "data": {"id": "list-1", "type": "IP_ADDRESS", "name": "Test", "entries": []}
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                lists = await client.traffic.get_all_lists("host-123", "site-1")
                # Returns empty since not a list
                assert lists == []


class TestACLAdditional:
    """Additional tests for ACL endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_acl_rules_single_item(self, auth: ApiKeyAuth) -> None:
        """Test ACL rules when data is a single dict."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*/ea/hosts/host-123/sites/site-1/acl-rules.*"),
                payload={
                    "data": {
                        "id": "acl-1",
                        "type": "IPV4",
                        "name": "Test",
                        "action": "BLOCK",
                        "enabled": True,
                        "index": 0,
                    }
                },
            )

            async with UniFiNetworkClient(auth=auth) as client:
                rules = await client.acl.get_all("host-123", "site-1")
                # Returns empty since not a list
                assert rules == []
