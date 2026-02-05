"""Tests for new Network API endpoints (vouchers, ACL, traffic, resources)."""

from __future__ import annotations

import re

import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth, ConnectionType
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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers.*"
                ),
                payload={
                    "data": [
                        {"id": "v-1", "code": "1234567890", "expired": False},
                        {"id": "v-2", "code": "0987654321", "expired": True},
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                vouchers = await client.vouchers.get_all("site-1")
                assert len(vouchers) == 2
                assert vouchers[0].code == "1234567890"
                assert vouchers[1].expired is True

    async def test_vouchers_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing vouchers with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                vouchers = await client.vouchers.get_all("site-1")
                assert vouchers == []

    async def test_vouchers_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific voucher."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers/v-1",
                payload={"data": {"id": "v-1", "code": "1234567890", "expired": False}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                voucher = await client.vouchers.get("site-1", "v-1")
                assert voucher.id == "v-1"
                assert voucher.code == "1234567890"

    async def test_vouchers_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting a voucher that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers/v-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.vouchers.get("site-1", "v-999")

    async def test_vouchers_create(self, auth: ApiKeyAuth) -> None:
        """Test creating vouchers."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers",
                payload={
                    "data": [
                        {"id": "v-1", "code": "1111111111", "expired": False},
                        {"id": "v-2", "code": "2222222222", "expired": False},
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                vouchers = await client.vouchers.create(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.vouchers.create("site-1", count=1)

    async def test_vouchers_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a voucher."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers/v-1",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.vouchers.delete("site-1", "v-1")
                assert result is True

    async def test_vouchers_delete_multiple(self, auth: ApiKeyAuth) -> None:
        """Test deleting multiple vouchers."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers/v-1",
                status=204,
            )
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers/v-2",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.vouchers.delete_multiple("site-1", ["v-1", "v-2"])
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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules.*"
                ),
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rules = await client.acl.get_all("site-1")
                assert len(rules) == 1
                assert rules[0].name == "Block Rule"
                assert rules[0].action == ACLAction.BLOCK

    async def test_acl_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing ACL rules with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rules = await client.acl.get_all("site-1")
                assert rules == []

    async def test_acl_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific ACL rule."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules/acl-1",
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.acl.get("site-1", "acl-1")
                assert rule.id == "acl-1"

    async def test_acl_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting an ACL rule that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules/acl-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.acl.get("site-1", "acl-999")

    async def test_acl_create(self, auth: ApiKeyAuth) -> None:
        """Test creating an ACL rule."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules",
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.acl.create(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.acl.create("site-1", name="Test", index=0)

    async def test_acl_update(self, auth: ApiKeyAuth) -> None:
        """Test updating an ACL rule."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules/acl-1",
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.acl.update("site-1", "acl-1", name="Updated Rule")
                assert rule.name == "Updated Rule"

    async def test_acl_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating an ACL rule failure."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules/acl-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.acl.update("site-1", "acl-1", name="Test")

    async def test_acl_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting an ACL rule."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules/acl-1",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.acl.delete("site-1", "acl-1")
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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists.*"
                ),
                payload={
                    "data": [
                        {"id": "list-1", "type": "IP_ADDRESS", "name": "Block List", "entries": []}
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                lists = await client.traffic.get_all_lists("site-1")
                assert len(lists) == 1
                assert lists[0].name == "Block List"

    async def test_traffic_get_all_lists_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing traffic matching lists with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                lists = await client.traffic.get_all_lists("site-1")
                assert lists == []

    async def test_traffic_get_list(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific traffic matching list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists/list-1",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Block List",
                        "entries": ["1.2.3.4"],
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                traffic_list = await client.traffic.get_list("site-1", "list-1")
                assert traffic_list.id == "list-1"
                assert traffic_list.entries == ["1.2.3.4"]

    async def test_traffic_get_list_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting a traffic matching list that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists/l-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.traffic.get_list("site-1", "l-999")

    async def test_traffic_create_list(self, auth: ApiKeyAuth) -> None:
        """Test creating a traffic matching list."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists",
                payload={
                    "data": {
                        "id": "list-new",
                        "type": "IP_ADDRESS",
                        "name": "New List",
                        "entries": [],
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                traffic_list = await client.traffic.create_list(
                    "site-1",
                    name="New List",
                    list_type=TrafficMatchingType.IP_ADDRESS,
                )
                assert traffic_list.id == "list-new"

    async def test_traffic_create_list_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating a traffic matching list failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.traffic.create_list(
                        "site-1", name="Test", list_type=TrafficMatchingType.IP_ADDRESS
                    )

    async def test_traffic_update_list(self, auth: ApiKeyAuth) -> None:
        """Test updating a traffic matching list."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists/list-1",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Updated List",
                        "entries": [],
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                traffic_list = await client.traffic.update_list(
                    "site-1", "list-1", name="Updated List"
                )
                assert traffic_list.name == "Updated List"

    async def test_traffic_update_list_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating a traffic matching list failure."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists/list-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.traffic.update_list("site-1", "list-1", name="Test")

    async def test_traffic_delete_list(self, auth: ApiKeyAuth) -> None:
        """Test deleting a traffic matching list."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists/list-1",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.traffic.delete_list("site-1", "list-1")
                assert result is True

    async def test_traffic_get_dpi_categories(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI categories."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/dpi/categories",
                payload={"data": [{"id": "cat-1", "name": "Streaming"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                categories = await client.traffic.get_dpi_categories("site-1")
                assert len(categories) == 1
                assert categories[0].name == "Streaming"

    async def test_traffic_get_dpi_categories_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI categories with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/dpi/categories",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                categories = await client.traffic.get_dpi_categories("site-1")
                assert categories == []

    async def test_traffic_get_dpi_applications(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI applications."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/dpi/applications",
                payload={"data": [{"id": "app-1", "name": "Netflix"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                apps = await client.traffic.get_dpi_applications("site-1")
                assert len(apps) == 1
                assert apps[0].name == "Netflix"

    async def test_traffic_get_dpi_applications_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting DPI applications with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/dpi/applications",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                apps = await client.traffic.get_dpi_applications("site-1")
                assert apps == []

    async def test_traffic_get_countries(self, auth: ApiKeyAuth) -> None:
        """Test getting countries."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/geo/countries",
                payload={"data": [{"code": "US", "name": "United States"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                countries = await client.traffic.get_countries("site-1")
                assert len(countries) == 1
                assert countries[0].code == "US"

    async def test_traffic_get_countries_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting countries with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/geo/countries",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                countries = await client.traffic.get_countries("site-1")
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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wan.*"
                ),
                payload={
                    "data": [{"id": "wan-1", "name": "WAN1", "status": "UP", "isPrimary": True}]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                interfaces = await client.resources.get_wan_interfaces("site-1")
                assert len(interfaces) == 1
                assert interfaces[0].name == "WAN1"
                assert interfaces[0].is_primary is True

    async def test_resources_get_wan_interfaces_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting WAN interfaces with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wan.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                interfaces = await client.resources.get_wan_interfaces("site-1")
                assert interfaces == []

    async def test_resources_get_vpn_tunnels(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN tunnels."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/vpn/tunnels.*"
                ),
                payload={"data": [{"id": "vpn-1", "name": "Site-to-Site VPN", "status": "UP"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert len(tunnels) == 1
                assert tunnels[0].name == "Site-to-Site VPN"

    async def test_resources_get_vpn_tunnels_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN tunnels with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/vpn/tunnels.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert tunnels == []

    async def test_resources_get_vpn_servers(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN servers."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/vpn/servers.*"
                ),
                payload={
                    "data": [
                        {"id": "srv-1", "name": "WireGuard", "type": "WIREGUARD", "enabled": True}
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert len(servers) == 1
                assert servers[0].name == "WireGuard"

    async def test_resources_get_vpn_servers_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting VPN servers with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/vpn/servers.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert servers == []

    async def test_resources_get_radius_profiles(self, auth: ApiKeyAuth) -> None:
        """Test getting RADIUS profiles."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/radius/profiles.*"
                ),
                payload={"data": [{"id": "rad-1", "name": "Corp RADIUS", "authPort": 1812}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert len(profiles) == 1
                assert profiles[0].name == "Corp RADIUS"

    async def test_resources_get_radius_profiles_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting RADIUS profiles with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/radius/profiles.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert profiles == []

    async def test_resources_get_device_tags(self, auth: ApiKeyAuth) -> None:
        """Test getting device tags."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/device-tags.*"
                ),
                payload={"data": [{"id": "tag-1", "name": "Production", "deviceCount": 5}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
                assert len(tags) == 1
                assert tags[0].name == "Production"
                assert tags[0].device_count == 5

    async def test_resources_get_device_tags_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting device tags with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/device-tags.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/application",
                payload={"data": {"version": "10.0.162", "name": "UniFi Network"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                info = await client.get_application_info()
                assert info["version"] == "10.0.162"

    async def test_get_application_info_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting application info with empty response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/application",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                info = await client.get_application_info()
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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers.*"
                ),
                payload={"data": [{"id": "v-1", "code": "123", "expired": False}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                vouchers = await client.vouchers.get_all("site-1", filter_str="active")
                assert len(vouchers) == 1

    async def test_vouchers_with_all_options(self, auth: ApiKeyAuth) -> None:
        """Test creating vouchers with all options."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers",
                payload={"data": [{"id": "v-1", "code": "123", "expired": False}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                vouchers = await client.vouchers.create(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/hotspot/vouchers",
                payload={"data": {"id": "v-1", "code": "123", "expired": False}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                vouchers = await client.vouchers.create("site-1", count=1)
                assert len(vouchers) == 1

    async def test_acl_with_filters(self, auth: ApiKeyAuth) -> None:
        """Test ACL with source and destination filters."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules",
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.acl.create(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Block",
                        "entries": ["1.2.3.4"],
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                lst = await client.traffic.create_list(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists/list-1",
                payload={
                    "data": {
                        "id": "list-1",
                        "type": "IP_ADDRESS",
                        "name": "Updated",
                        "entries": ["1.2.3.4", "5.6.7.8"],
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                lst = await client.traffic.update_list(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules/acl-1",
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.acl.update(
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/protect/integration/v1/sites/site-1/viewers",
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

            async with UniFiProtectClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                viewers = await client.viewers.get_all("site-1")
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/devices/dev-1/locate",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.devices.locate("site-1", "dev-1", enabled=True)
                assert result is True

    async def test_device_get_pending_adoption(self, auth: ApiKeyAuth) -> None:
        """Test getting devices pending adoption."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/pending-devices",
                payload={"data": [{"id": "dev-1", "mac": "aa:bb:cc:dd:ee:ff"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                devices = await client.devices.get_pending_adoption()
                assert len(devices) == 1

    async def test_device_get_pending_adoption_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting devices pending adoption when empty."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/pending-devices",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                devices = await client.devices.get_pending_adoption()
                assert devices == []

    async def test_device_get_statistics(self, auth: ApiKeyAuth) -> None:
        """Test getting device statistics."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/devices/dev-1/statistics/latest",
                payload={"data": {"cpu": 25, "memory": 50}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                stats = await client.devices.get_statistics("site-1", "dev-1")
                assert stats["cpu"] == 25

    async def test_device_get_statistics_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting device statistics when empty."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/devices/dev-1/statistics/latest",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                stats = await client.devices.get_statistics("site-1", "dev-1")
                assert stats == {}

    async def test_device_port_action(self, auth: ApiKeyAuth) -> None:
        """Test device port action."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/devices/dev-1/ports/1",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.devices.execute_port_action(
                    "site-1", "dev-1", 1, poe_mode="auto", speed="1000", enabled=True
                )
                assert result is True

    async def test_device_port_action_no_settings(self, auth: ApiKeyAuth) -> None:
        """Test device port action without settings raises error."""
        async with UniFiNetworkClient(
            auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
        ) as client:
            with pytest.raises(ValueError, match="At least one"):
                await client.devices.execute_port_action("site-1", "dev-1", 1)

    async def test_device_execute_action(self, auth: ApiKeyAuth) -> None:
        """Test device execute action."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/devices/dev-1/provision",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.devices.execute_action("site-1", "dev-1", "provision")
                assert result is True

    async def test_device_execute_action_invalid(self, auth: ApiKeyAuth) -> None:
        """Test device execute action with invalid action."""
        async with UniFiNetworkClient(
            auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
        ) as client:
            with pytest.raises(ValueError, match="Action must be one of"):
                await client.devices.execute_action("site-1", "dev-1", "invalid")


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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/clients/aa:bb:cc:dd:ee:ff",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.clients.forget("site-1", "aa:bb:cc:dd:ee:ff")
                assert result is True

    async def test_client_execute_action(self, auth: ApiKeyAuth) -> None:
        """Test client execute action."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/clients/aa:bb:cc:dd:ee:ff/block",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.clients.execute_action("site-1", "aa:bb:cc:dd:ee:ff", "block")
                assert result is True

    async def test_client_execute_action_invalid(self, auth: ApiKeyAuth) -> None:
        """Test client execute action with invalid action."""
        async with UniFiNetworkClient(
            auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
        ) as client:
            with pytest.raises(ValueError, match="Action must be one of"):
                await client.clients.execute_action("site-1", "aa:bb:cc:dd:ee:ff", "invalid")


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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wan.*"
                ),
                payload={"data": {"id": "wan-1", "name": "WAN1"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                interfaces = await client.resources.get_wan_interfaces("site-1")
                # Returns empty since not a list
                assert interfaces == []

    async def test_vpn_tunnels_single_item(self, auth: ApiKeyAuth) -> None:
        """Test VPN tunnels when data is a single dict."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/vpn/tunnels.*"
                ),
                payload={"data": {"id": "vpn-1", "name": "VPN1"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
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
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/dpi/categories",
                payload={"data": {"id": "cat-1", "name": "Test"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                categories = await client.traffic.get_dpi_categories("site-1")
                # Returns empty since not a list
                assert categories == []

    async def test_dpi_applications_single_item(self, auth: ApiKeyAuth) -> None:
        """Test DPI applications when data is a single dict."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/dpi/applications",
                payload={"data": {"id": "app-1", "name": "Test"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                apps = await client.traffic.get_dpi_applications("site-1")
                # Returns empty since not a list
                assert apps == []

    async def test_countries_single_item(self, auth: ApiKeyAuth) -> None:
        """Test countries when data is a single dict."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/geo/countries",
                payload={"data": {"code": "US", "name": "USA"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                countries = await client.traffic.get_countries("site-1")
                # Returns empty since not a list
                assert countries == []

    async def test_traffic_lists_single_item(self, auth: ApiKeyAuth) -> None:
        """Test traffic lists when data is a single dict."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/traffic-matching-lists.*"
                ),
                payload={
                    "data": {"id": "list-1", "type": "IP_ADDRESS", "name": "Test", "entries": []}
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                lists = await client.traffic.get_all_lists("site-1")
                # Returns empty since not a list
                assert lists == []


class TestFirewallEndpoint:
    """Tests for firewall endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_firewall_list_zones(self, auth: ApiKeyAuth) -> None:
        """Test listing firewall zones."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones.*"
                ),
                payload={
                    "data": [
                        {"id": "zone-1", "name": "Internal", "zoneKey": "INTERNAL"},
                        {"id": "zone-2", "name": "External", "zoneKey": "EXTERNAL"},
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                zones = await client.firewall.list_zones("site-1")
                assert len(zones) == 2
                assert zones[0].name == "Internal"

    async def test_firewall_list_zones_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing firewall zones with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                zones = await client.firewall.list_zones("site-1")
                assert zones == []

    async def test_firewall_get_zone(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific firewall zone."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones/zone-1",
                payload={"data": {"id": "zone-1", "name": "Internal", "zoneKey": "INTERNAL"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                zone = await client.firewall.get_zone("site-1", "zone-1")
                assert zone.id == "zone-1"
                assert zone.name == "Internal"

    async def test_firewall_get_zone_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting a firewall zone that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones/zone-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.firewall.get_zone("site-1", "zone-999")

    async def test_firewall_create_zone(self, auth: ApiKeyAuth) -> None:
        """Test creating a firewall zone."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones",
                payload={"data": {"id": "zone-new", "name": "Custom Zone", "zoneKey": "CUSTOM"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                zone = await client.firewall.create_zone("site-1", name="Custom Zone")
                assert zone.id == "zone-new"
                assert zone.name == "Custom Zone"

    async def test_firewall_create_zone_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating a firewall zone failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.firewall.create_zone("site-1", name="Test")

    async def test_firewall_update_zone(self, auth: ApiKeyAuth) -> None:
        """Test updating a firewall zone."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones/zone-1",
                payload={"data": {"id": "zone-1", "name": "Updated Zone", "zoneKey": "CUSTOM"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                zone = await client.firewall.update_zone("site-1", "zone-1", name="Updated Zone")
                assert zone.name == "Updated Zone"

    async def test_firewall_update_zone_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating a firewall zone failure."""
        with aioresponses() as m:
            m.put(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones/zone-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.firewall.update_zone("site-1", "zone-1", name="Test")

    async def test_firewall_delete_zone(self, auth: ApiKeyAuth) -> None:
        """Test deleting a firewall zone."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/zones/zone-1",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.firewall.delete_zone("site-1", "zone-1")
                assert result is True

    async def test_firewall_list_rules(self, auth: ApiKeyAuth) -> None:
        """Test listing firewall rules."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies.*"
                ),
                payload={
                    "data": [
                        {
                            "id": "rule-1",
                            "name": "Block All",
                            "action": "drop",
                            "protocol": "all",
                        }
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rules = await client.firewall.list_rules("site-1")
                assert len(rules) == 1
                assert rules[0].name == "Block All"

    async def test_firewall_list_rules_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing firewall rules with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies.*"
                ),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rules = await client.firewall.list_rules("site-1")
                assert rules == []

    async def test_firewall_get_rule(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific firewall rule."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies/rule-1",
                payload={
                    "data": {
                        "id": "rule-1",
                        "name": "Block All",
                        "action": "drop",
                        "protocol": "all",
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.firewall.get_rule("site-1", "rule-1")
                assert rule.id == "rule-1"

    async def test_firewall_get_rule_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting a firewall rule that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies/rule-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.firewall.get_rule("site-1", "rule-999")

    async def test_firewall_create_rule(self, auth: ApiKeyAuth) -> None:
        """Test creating a firewall rule."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies",
                payload={
                    "data": {
                        "id": "rule-new",
                        "name": "New Rule",
                        "action": "drop",
                        "protocol": "tcp",
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.firewall.create_rule(
                    "site-1",
                    name="New Rule",
                    action="drop",
                    protocol="tcp",
                )
                assert rule.id == "rule-new"

    async def test_firewall_create_rule_failed(self, auth: ApiKeyAuth) -> None:
        """Test creating a firewall rule failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.firewall.create_rule("site-1", name="Test")

    async def test_firewall_update_rule(self, auth: ApiKeyAuth) -> None:
        """Test updating a firewall rule."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies/rule-1",
                payload={
                    "data": {
                        "id": "rule-1",
                        "name": "Updated Rule",
                        "action": "accept",
                        "protocol": "all",
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rule = await client.firewall.update_rule("site-1", "rule-1", name="Updated Rule")
                assert rule.name == "Updated Rule"

    async def test_firewall_update_rule_failed(self, auth: ApiKeyAuth) -> None:
        """Test updating a firewall rule failure."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies/rule-1",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed"):
                    await client.firewall.update_rule("site-1", "rule-1", name="Test")

    async def test_firewall_delete_rule(self, auth: ApiKeyAuth) -> None:
        """Test deleting a firewall rule."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/firewall/policies/rule-1",
                status=204,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.firewall.delete_rule("site-1", "rule-1")
                assert result is True


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
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/acl-rules.*"
                ),
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

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                rules = await client.acl.get_all("site-1")
                # Returns empty since not a list
                assert rules == []


class TestWifiEndpoint:
    """Tests for WiFi endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_wifi_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing WiFi networks."""
        with aioresponses() as m:
            m.get(
                re.compile(
                    r".*/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts.*"
                ),
                payload={
                    "data": [
                        {"id": "wifi-1", "name": "Guest WiFi", "ssid": "Guest", "security": "wpa2"},
                        {"id": "wifi-2", "name": "Main WiFi", "ssid": "Main", "security": "wpa3"},
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi_networks = await client.wifi.get_all("site-1")
                assert len(wifi_networks) == 2
                assert wifi_networks[0].name == "Guest WiFi"
                assert wifi_networks[1].ssid == "Main"

    async def test_wifi_get_all_with_params(self, auth: ApiKeyAuth) -> None:
        """Test listing WiFi networks with pagination and filter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wifi/broadcasts\?.*"),
                payload={"data": [{"id": "wifi-1", "name": "Test WiFi", "ssid": "Test", "security": "wpa2"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi_networks = await client.wifi.get_all("site-1", offset=10, limit=20, filter_str="test")
                assert len(wifi_networks) == 1

    async def test_wifi_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing WiFi networks with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wifi/broadcasts.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi_networks = await client.wifi.get_all("site-1")
                assert wifi_networks == []

    async def test_wifi_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test listing WiFi networks with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wifi/broadcasts.*"),
                payload=None,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi_networks = await client.wifi.get_all("site-1")
                assert wifi_networks == []

    async def test_wifi_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific WiFi network."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts/wifi-1",
                payload={"data": {"id": "wifi-1", "name": "Guest WiFi", "ssid": "Guest", "security": "wpa2"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi = await client.wifi.get("site-1", "wifi-1")
                assert wifi.id == "wifi-1"
                assert wifi.name == "Guest WiFi"

    async def test_wifi_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting WiFi when response is a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts/wifi-1",
                payload={"data": [{"id": "wifi-1", "name": "Guest WiFi", "ssid": "Guest", "security": "wpa2"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi = await client.wifi.get("site-1", "wifi-1")
                assert wifi.id == "wifi-1"

    async def test_wifi_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting WiFi network that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts/wifi-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.wifi.get("site-1", "wifi-999")

    async def test_wifi_create(self, auth: ApiKeyAuth) -> None:
        """Test creating a WiFi network."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts",
                payload={
                    "data": {
                        "id": "wifi-new",
                        "name": "New WiFi",
                        "ssid": "NewSSID",
                        "security": "wpa2",
                        "hidden": False,
                    }
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                from unifi_official_api.network.models import WifiSecurity

                wifi = await client.wifi.create(
                    "site-1", name="New WiFi", ssid="NewSSID", passphrase="password123", security=WifiSecurity.WPA2
                )
                assert wifi.id == "wifi-new"
                assert wifi.name == "New WiFi"

    async def test_wifi_create_with_network_id(self, auth: ApiKeyAuth) -> None:
        """Test creating WiFi with network_id."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts",
                payload={"data": {"id": "wifi-new", "name": "New", "ssid": "New", "security": "wpa2", "networkId": "net-1"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                from unifi_official_api.network.models import WifiSecurity

                wifi = await client.wifi.create("site-1", name="New", ssid="New", network_id="net-1")
                assert wifi.id == "wifi-new"

    async def test_wifi_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test WiFi creation failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts",
                payload=[],  # Empty list response
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed to create"):
                    await client.wifi.create("site-1", name="New", ssid="New")

    async def test_wifi_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a WiFi network."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts/wifi-1",
                payload={"data": {"id": "wifi-1", "name": "Updated WiFi", "ssid": "Updated", "security": "wpa3"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wifi = await client.wifi.update("site-1", "wifi-1", name="Updated WiFi")
                assert wifi.name == "Updated WiFi"

    async def test_wifi_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test WiFi update failure."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts/wifi-1",
                payload=[],  # Empty list response
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed to update"):
                    await client.wifi.update("site-1", "wifi-1", name="Updated")

    async def test_wifi_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a WiFi network."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/wifi/broadcasts/wifi-1",
                payload={},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.wifi.delete("site-1", "wifi-1")
                assert result is True


class TestNetworksEndpoint:
    """Tests for Networks endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_networks_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing networks."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*sites/site-1/networks.*"),
                payload={
                    "data": [
                        {"id": "net-1", "name": "Corporate", "type": "corporate"},
                        {"id": "net-2", "name": "WAN", "type": "wan"},
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                networks = await client.networks.get_all("site-1")
                assert len(networks) == 2
                assert networks[0].name == "Corporate"

    async def test_networks_get_all_with_params(self, auth: ApiKeyAuth) -> None:
        """Test listing networks with pagination."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*networks\?.*"),
                payload={"data": [{"id": "net-1", "name": "Corporate", "type": "corporate"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                networks = await client.networks.get_all("site-1", offset=5, limit=10, filter_str="corporate")
                assert len(networks) == 1

    async def test_networks_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing networks with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*networks.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                networks = await client.networks.get_all("site-1")
                assert networks == []

    async def test_networks_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific network."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1",
                payload={"data": {"id": "net-1", "name": "Corporate", "type": "corporate"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                network = await client.networks.get("site-1", "net-1")
                assert network.id == "net-1"
                assert network.name == "Corporate"

    async def test_networks_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting network when response is a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1",
                payload={"data": [{"id": "net-1", "name": "Corporate", "type": "corporate"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                network = await client.networks.get("site-1", "net-1")
                assert network.id == "net-1"

    async def test_networks_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting network that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.networks.get("site-1", "net-999")

    async def test_networks_create(self, auth: ApiKeyAuth) -> None:
        """Test creating a network."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks",
                payload={"data": {"id": "net-new", "name": "New Network", "type": "guest"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                from unifi_official_api.network.models import NetworkType

                network = await client.networks.create("site-1", name="New Network", type=NetworkType.GUEST)
                assert network.id == "net-new"
                assert network.name == "New Network"

    async def test_networks_create_failed(self, auth: ApiKeyAuth) -> None:
        """Test network creation failure."""
        with aioresponses() as m:
            m.post(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks",
                payload=[],  # Empty list response
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                from unifi_official_api.network.models import NetworkType

                with pytest.raises(ValueError, match="Failed to create"):
                    await client.networks.create("site-1", name="New", type=NetworkType.CORPORATE)

    async def test_networks_update(self, auth: ApiKeyAuth) -> None:
        """Test updating a network."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1",
                payload={"data": {"id": "net-1", "name": "Updated Network", "type": "corporate"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                network = await client.networks.update("site-1", "net-1", name="Updated Network")
                assert network.name == "Updated Network"

    async def test_networks_update_failed(self, auth: ApiKeyAuth) -> None:
        """Test network update failure."""
        with aioresponses() as m:
            m.patch(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1",
                payload=[],  # Empty list response
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="Failed to update"):
                    await client.networks.update("site-1", "net-1", name="Updated")

    async def test_networks_delete(self, auth: ApiKeyAuth) -> None:
        """Test deleting a network."""
        with aioresponses() as m:
            m.delete(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1",
                payload={},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                result = await client.networks.delete("site-1", "net-1")
                assert result is True

    async def test_networks_get_references(self, auth: ApiKeyAuth) -> None:
        """Test getting network references."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1/references",
                payload={"data": {"devices": ["dev-1"], "wifi": ["wifi-1"]}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                refs = await client.networks.get_references("site-1", "net-1")
                assert refs == {"devices": ["dev-1"], "wifi": ["wifi-1"]}

    async def test_networks_get_references_empty(self, auth: ApiKeyAuth) -> None:
        """Test getting network references with empty/invalid response."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1/networks/net-1/references",
                payload=[],  # Empty list response returns empty dict
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                refs = await client.networks.get_references("site-1", "net-1")
                assert refs == {}


class TestSitesEndpoint:
    """Tests for Sites endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    async def test_sites_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing sites."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*sites.*"),
                payload={
                    "data": [
                        {"id": "site-1", "name": "Default", "desc": "Default site"},
                        {"id": "site-2", "name": "Branch", "desc": "Branch office"},
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                sites = await client.sites.get_all()
                assert len(sites) == 2
                assert sites[0].name == "Default"

    async def test_sites_get_all_with_params(self, auth: ApiKeyAuth) -> None:
        """Test listing sites with pagination."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*sites\?.*"),
                payload={"data": [{"id": "site-2", "name": "Branch", "desc": "Branch office"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                sites = await client.sites.get_all(offset=1, limit=5, filter_str="branch")
                assert len(sites) == 1

    async def test_sites_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing sites with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*sites.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                sites = await client.sites.get_all()
                assert sites == []

    async def test_sites_get(self, auth: ApiKeyAuth) -> None:
        """Test getting a specific site."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1",
                payload={"data": {"id": "site-1", "name": "Default", "desc": "Default site"}},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                site = await client.sites.get("site-1")
                assert site.id == "site-1"
                assert site.name == "Default"

    async def test_sites_get_list_response(self, auth: ApiKeyAuth) -> None:
        """Test getting site when response is a list."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-1",
                payload={"data": [{"id": "site-1", "name": "Default", "desc": "Default site"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                site = await client.sites.get("site-1")
                assert site.id == "site-1"

    async def test_sites_get_not_found(self, auth: ApiKeyAuth) -> None:
        """Test getting site that doesn't exist."""
        with aioresponses() as m:
            m.get(
                "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/site-999",
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                with pytest.raises(ValueError, match="not found"):
                    await client.sites.get("site-999")


class TestResourcesComprehensive:
    """Comprehensive tests for resources endpoint."""

    @pytest.fixture
    def auth(self) -> ApiKeyAuth:
        """Create test auth."""
        return ApiKeyAuth(api_key="test-api-key")

    # WAN Interfaces Tests

    async def test_wan_interfaces_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*sites/site-1/wans.*"),
                payload={
                    "data": [
                        {
                            "id": "wan-1",
                            "name": "WAN1",
                            "status": "UP",
                            "ipAddress": "1.2.3.4",
                            "isPrimary": True,
                            "isConnected": True,
                        },
                        {
                            "id": "wan-2",
                            "name": "WAN2",
                            "status": "DOWN",
                            "ipAddress": "5.6.7.8",
                            "isPrimary": False,
                            "isConnected": False,
                        },
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1")
                assert len(wan_interfaces) == 2
                assert wan_interfaces[0].id == "wan-1"
                assert wan_interfaces[0].name == "WAN1"
                assert wan_interfaces[0].is_primary is True
                assert wan_interfaces[1].id == "wan-2"
                assert wan_interfaces[1].is_connected is False

    async def test_wan_interfaces_get_all_with_offset(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with offset parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans\?.*offset=10.*"),
                payload={"data": [{"id": "wan-1", "name": "WAN1"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1", offset=10)
                assert len(wan_interfaces) == 1

    async def test_wan_interfaces_get_all_with_limit(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with limit parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans\?.*limit=5.*"),
                payload={"data": [{"id": "wan-1", "name": "WAN1"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1", limit=5)
                assert len(wan_interfaces) == 1

    async def test_wan_interfaces_get_all_with_filter(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with filter parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans\?.*filter=.*"),
                payload={"data": [{"id": "wan-1", "name": "WAN1"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1", filter_str="status==UP")
                assert len(wan_interfaces) == 1

    async def test_wan_interfaces_get_all_with_all_params(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with all parameters."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans\?.*"),
                payload={"data": [{"id": "wan-1", "name": "WAN1"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces(
                    "site-1", offset=10, limit=20, filter_str="status==UP"
                )
                assert len(wan_interfaces) == 1

    async def test_wan_interfaces_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1")
                assert wan_interfaces == []

    async def test_wan_interfaces_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans.*"),
                payload=None,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1")
                assert wan_interfaces == []

    async def test_wan_interfaces_get_all_raw_list(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with raw list response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans.*"),
                payload=[{"id": "wan-1", "name": "WAN1"}],
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1")
                assert len(wan_interfaces) == 1
                assert wan_interfaces[0].id == "wan-1"

    # VPN Tunnels Tests

    async def test_vpn_tunnels_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels.*"),
                payload={
                    "data": [
                        {
                            "id": "tunnel-1",
                            "name": "Site A to Site B",
                            "status": "UP",
                            "localNetwork": "192.168.1.0/24",
                            "remoteNetwork": "192.168.2.0/24",
                            "remoteIp": "203.0.113.1",
                        },
                        {
                            "id": "tunnel-2",
                            "name": "Site B to Site C",
                            "status": "DOWN",
                        },
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert len(tunnels) == 2
                assert tunnels[0].id == "tunnel-1"
                assert tunnels[0].name == "Site A to Site B"
                assert tunnels[1].status.value == "DOWN"

    async def test_vpn_tunnels_get_all_with_offset(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with offset parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels\?.*offset=5.*"),
                payload={"data": [{"id": "tunnel-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1", offset=5)
                assert len(tunnels) == 1

    async def test_vpn_tunnels_get_all_with_limit(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with limit parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels\?.*limit=10.*"),
                payload={"data": [{"id": "tunnel-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1", limit=10)
                assert len(tunnels) == 1

    async def test_vpn_tunnels_get_all_with_filter(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with filter parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels\?.*filter=.*"),
                payload={"data": [{"id": "tunnel-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1", filter_str="status==UP")
                assert len(tunnels) == 1

    async def test_vpn_tunnels_get_all_with_all_params(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with all parameters."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels\?.*"),
                payload={"data": [{"id": "tunnel-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels(
                    "site-1", offset=5, limit=15, filter_str="status==UP"
                )
                assert len(tunnels) == 1

    async def test_vpn_tunnels_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert tunnels == []

    async def test_vpn_tunnels_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels.*"),
                payload=None,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert tunnels == []

    async def test_vpn_tunnels_get_all_raw_list(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with raw list response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels.*"),
                payload=[{"id": "tunnel-1", "name": "Test"}],
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert len(tunnels) == 1
                assert tunnels[0].id == "tunnel-1"

    # VPN Servers Tests

    async def test_vpn_servers_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers.*"),
                payload={
                    "data": [
                        {
                            "id": "server-1",
                            "name": "WireGuard VPN",
                            "type": "WIREGUARD",
                            "enabled": True,
                            "port": 51820,
                            "network": "10.8.0.0/24",
                        },
                        {
                            "id": "server-2",
                            "name": "OpenVPN Server",
                            "type": "OPENVPN",
                            "enabled": False,
                            "port": 1194,
                        },
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert len(servers) == 2
                assert servers[0].id == "server-1"
                assert servers[0].name == "WireGuard VPN"
                assert servers[0].enabled is True
                assert servers[1].type == "OPENVPN"

    async def test_vpn_servers_get_all_with_offset(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with offset parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers\?.*offset=3.*"),
                payload={"data": [{"id": "server-1", "name": "Test", "enabled": True}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1", offset=3)
                assert len(servers) == 1

    async def test_vpn_servers_get_all_with_limit(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with limit parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers\?.*limit=8.*"),
                payload={"data": [{"id": "server-1", "name": "Test", "enabled": True}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1", limit=8)
                assert len(servers) == 1

    async def test_vpn_servers_get_all_with_filter(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with filter parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers\?.*filter=.*"),
                payload={"data": [{"id": "server-1", "name": "Test", "enabled": True}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1", filter_str="enabled==true")
                assert len(servers) == 1

    async def test_vpn_servers_get_all_with_all_params(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with all parameters."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers\?.*"),
                payload={"data": [{"id": "server-1", "name": "Test", "enabled": True}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers(
                    "site-1", offset=3, limit=12, filter_str="enabled==true"
                )
                assert len(servers) == 1

    async def test_vpn_servers_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert servers == []

    async def test_vpn_servers_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers.*"),
                payload=None,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert servers == []

    async def test_vpn_servers_get_all_raw_list(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with raw list response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers.*"),
                payload=[{"id": "server-1", "name": "Test", "enabled": True}],
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert len(servers) == 1
                assert servers[0].id == "server-1"

    # RADIUS Profiles Tests

    async def test_radius_profiles_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles.*"),
                payload={
                    "data": [
                        {
                            "id": "radius-1",
                            "name": "Primary RADIUS",
                            "authServer": "radius1.example.com",
                            "authPort": 1812,
                            "acctServer": "radius1.example.com",
                            "acctPort": 1813,
                            "enabled": True,
                        },
                        {
                            "id": "radius-2",
                            "name": "Secondary RADIUS",
                            "authServer": "radius2.example.com",
                            "enabled": False,
                        },
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert len(profiles) == 2
                assert profiles[0].id == "radius-1"
                assert profiles[0].name == "Primary RADIUS"
                assert profiles[0].auth_server == "radius1.example.com"
                assert profiles[0].enabled is True
                assert profiles[1].enabled is False

    async def test_radius_profiles_get_all_with_offset(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with offset parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles\?.*offset=2.*"),
                payload={"data": [{"id": "radius-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1", offset=2)
                assert len(profiles) == 1

    async def test_radius_profiles_get_all_with_limit(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with limit parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles\?.*limit=6.*"),
                payload={"data": [{"id": "radius-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1", limit=6)
                assert len(profiles) == 1

    async def test_radius_profiles_get_all_with_filter(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with filter parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles\?.*filter=.*"),
                payload={"data": [{"id": "radius-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1", filter_str="enabled==true")
                assert len(profiles) == 1

    async def test_radius_profiles_get_all_with_all_params(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with all parameters."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles\?.*"),
                payload={"data": [{"id": "radius-1", "name": "Test"}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles(
                    "site-1", offset=2, limit=9, filter_str="enabled==true"
                )
                assert len(profiles) == 1

    async def test_radius_profiles_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert profiles == []

    async def test_radius_profiles_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles.*"),
                payload=None,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert profiles == []

    async def test_radius_profiles_get_all_raw_list(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with raw list response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles.*"),
                payload=[{"id": "radius-1", "name": "Test"}],
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert len(profiles) == 1
                assert profiles[0].id == "radius-1"

    # Device Tags Tests

    async def test_device_tags_get_all(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags.*"),
                payload={
                    "data": [
                        {
                            "id": "tag-1",
                            "name": "Production",
                            "color": "#FF0000",
                            "deviceCount": 15,
                        },
                        {
                            "id": "tag-2",
                            "name": "Staging",
                            "color": "#00FF00",
                            "deviceCount": 5,
                        },
                    ]
                },
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
                assert len(tags) == 2
                assert tags[0].id == "tag-1"
                assert tags[0].name == "Production"
                assert tags[0].color == "#FF0000"
                assert tags[0].device_count == 15
                assert tags[1].device_count == 5

    async def test_device_tags_get_all_with_offset(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with offset parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags\?.*offset=1.*"),
                payload={"data": [{"id": "tag-1", "name": "Test", "deviceCount": 0}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1", offset=1)
                assert len(tags) == 1

    async def test_device_tags_get_all_with_limit(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with limit parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags\?.*limit=3.*"),
                payload={"data": [{"id": "tag-1", "name": "Test", "deviceCount": 0}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1", limit=3)
                assert len(tags) == 1

    async def test_device_tags_get_all_with_filter(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with filter parameter."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags\?.*filter=.*"),
                payload={"data": [{"id": "tag-1", "name": "Test", "deviceCount": 0}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1", filter_str="name==Production")
                assert len(tags) == 1

    async def test_device_tags_get_all_with_all_params(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with all parameters."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags\?.*"),
                payload={"data": [{"id": "tag-1", "name": "Test", "deviceCount": 0}]},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags(
                    "site-1", offset=1, limit=7, filter_str="name==Production"
                )
                assert len(tags) == 1

    async def test_device_tags_get_all_empty(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with empty response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags.*"),
                payload={"data": []},
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
                assert tags == []

    async def test_device_tags_get_all_none_response(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with None response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags.*"),
                payload=None,
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
                assert tags == []

    async def test_device_tags_get_all_raw_list(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with raw list response."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags.*"),
                payload=[{"id": "tag-1", "name": "Test", "deviceCount": 0}],
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
                assert len(tags) == 1
                assert tags[0].id == "tag-1"

    async def test_wan_interfaces_invalid_data_format(self, auth: ApiKeyAuth) -> None:
        """Test listing WAN interfaces with invalid data format (not a list)."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*wans.*"),
                payload={"data": {"id": "wan-1"}},  # Data is a dict, not a list
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                wan_interfaces = await client.resources.get_wan_interfaces("site-1")
                assert wan_interfaces == []

    async def test_vpn_tunnels_invalid_data_format(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN tunnels with invalid data format (not a list)."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/tunnels.*"),
                payload={"data": {"id": "tunnel-1"}},  # Data is a dict, not a list
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tunnels = await client.resources.get_vpn_tunnels("site-1")
                assert tunnels == []

    async def test_vpn_servers_invalid_data_format(self, auth: ApiKeyAuth) -> None:
        """Test listing VPN servers with invalid data format (not a list)."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*vpn/servers.*"),
                payload={"data": {"id": "server-1"}},  # Data is a dict, not a list
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                servers = await client.resources.get_vpn_servers("site-1")
                assert servers == []

    async def test_radius_profiles_invalid_data_format(self, auth: ApiKeyAuth) -> None:
        """Test listing RADIUS profiles with invalid data format (not a list)."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*radius/profiles.*"),
                payload={"data": {"id": "radius-1"}},  # Data is a dict, not a list
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                profiles = await client.resources.get_radius_profiles("site-1")
                assert profiles == []

    async def test_device_tags_invalid_data_format(self, auth: ApiKeyAuth) -> None:
        """Test listing device tags with invalid data format (not a list)."""
        with aioresponses() as m:
            m.get(
                re.compile(r".*device-tags.*"),
                payload={"data": {"id": "tag-1"}},  # Data is a dict, not a list
            )

            async with UniFiNetworkClient(
                auth=auth, connection_type=ConnectionType.REMOTE, console_id="test-console-id"
            ) as client:
                tags = await client.resources.get_device_tags("site-1")
                assert tags == []
