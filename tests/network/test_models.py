"""Tests for UniFi Network models."""

from __future__ import annotations

from unifi_official_api.network import (
    Client,
    ClientType,
    Device,
    DeviceState,
    DeviceType,
    Network,
    NetworkPurpose,
    NetworkType,
    Site,
    WifiNetwork,
    WifiSecurity,
)


class TestDeviceModel:
    """Tests for Device model."""

    def test_create_device(self) -> None:
        """Test creating a device from dict."""
        data = {
            "id": "dev-123",
            "mac": "00:11:22:33:44:55",
            "name": "Test Device",
            "type": "usw",
            "state": "connected",
        }
        device = Device.model_validate(data)
        assert device.id == "dev-123"
        assert device.mac == "00:11:22:33:44:55"
        assert device.name == "Test Device"
        assert device.type == DeviceType.USW
        assert device.state == DeviceState.CONNECTED

    def test_device_with_alias_fields(self) -> None:
        """Test device with aliased field names."""
        data = {
            "id": "dev-123",
            "mac": "00:11:22:33:44:55",
            "firmwareVersion": "6.5.28",
            "siteId": "site-123",
        }
        device = Device.model_validate(data)
        assert device.firmware_version == "6.5.28"
        assert device.site_id == "site-123"


class TestClientModel:
    """Tests for Client model."""

    def test_create_client(self) -> None:
        """Test creating a client from dict."""
        data = {
            "id": "client-123",
            "mac": "AA:BB:CC:DD:EE:FF",
            "name": "My Phone",
            "type": "wireless",
        }
        client = Client.model_validate(data)
        assert client.id == "client-123"
        assert client.name == "My Phone"
        assert client.type == ClientType.WIRELESS

    def test_client_display_name(self) -> None:
        """Test client display_name property."""
        # With name
        client = Client.model_validate(
            {
                "id": "1",
                "mac": "AA:BB:CC:DD:EE:FF",
                "name": "Custom Name",
            }
        )
        assert client.display_name == "Custom Name"

        # With hostname only
        client = Client.model_validate(
            {
                "id": "2",
                "mac": "AA:BB:CC:DD:EE:FF",
                "hostname": "device-hostname",
            }
        )
        assert client.display_name == "device-hostname"

        # MAC only
        client = Client.model_validate(
            {
                "id": "3",
                "mac": "AA:BB:CC:DD:EE:FF",
            }
        )
        assert client.display_name == "AA:BB:CC:DD:EE:FF"


class TestNetworkModel:
    """Tests for Network model."""

    def test_create_network(self) -> None:
        """Test creating a network from dict."""
        data = {
            "id": "net-123",
            "name": "Corporate",
            "type": "corporate",
            "purpose": "corporate",
            "vlanId": 10,
            "subnet": "192.168.10.0/24",
        }
        network = Network.model_validate(data)
        assert network.id == "net-123"
        assert network.name == "Corporate"
        assert network.type == NetworkType.CORPORATE
        assert network.purpose == NetworkPurpose.CORPORATE
        assert network.vlan_id == 10


class TestWifiNetworkModel:
    """Tests for WifiNetwork model."""

    def test_create_wifi_network(self) -> None:
        """Test creating a WiFi network from dict."""
        data = {
            "id": "wifi-123",
            "name": "Home WiFi",
            "ssid": "MyNetwork",
            "security": "wpa2",
            "hidden": False,
        }
        wifi = WifiNetwork.model_validate(data)
        assert wifi.id == "wifi-123"
        assert wifi.ssid == "MyNetwork"
        assert wifi.security == WifiSecurity.WPA2
        assert wifi.hidden is False


class TestSiteModel:
    """Tests for Site model."""

    def test_create_site(self) -> None:
        """Test creating a site from dict."""
        data = {
            "id": "site-123",
            "name": "Main Office",
            "deviceCount": 25,
            "clientCount": 100,
        }
        site = Site.model_validate(data)
        assert site.id == "site-123"
        assert site.name == "Main Office"
        assert site.device_count == 25
        assert site.client_count == 100


class TestDNSPolicyModel:
    """Tests for DNS Policy model."""

    def test_create_dns_policy(self) -> None:
        """Test creating a DNS policy from dict."""
        from unifi_official_api.network.models.dns import DNSPolicy, DNSRecordType

        data = {
            "id": "dns-1",
            "type": "A_RECORD",
            "enabled": True,
            "domain": "test.local",
            "ipv4Address": "192.168.1.100",
            "ttlSeconds": 300,
        }
        policy = DNSPolicy.model_validate(data)
        assert policy.id == "dns-1"
        assert policy.type == DNSRecordType.A_RECORD
        assert policy.enabled is True
        assert policy.domain == "test.local"
        assert policy.ipv4_address == "192.168.1.100"
        assert policy.ttl_seconds == 300

    def test_dns_policy_with_metadata(self) -> None:
        """Test DNS policy with metadata."""
        from unifi_official_api.network.models.dns import DNSPolicy

        data = {
            "id": "dns-2",
            "type": "CNAME_RECORD",
            "enabled": False,
            "domain": "alias.local",
            "metadata": {"origin": "USER_DEFINED"},
        }
        policy = DNSPolicy.model_validate(data)
        assert policy.metadata is not None
        assert policy.metadata.origin == "USER_DEFINED"

    def test_dns_policy_extra_fields(self) -> None:
        """Test DNS policy allows extra fields."""
        from unifi_official_api.network.models.dns import DNSPolicy

        data = {
            "id": "dns-3",
            "type": "A_RECORD",
            "enabled": True,
            "domain": "extra.local",
            "unknownField": "value",
        }
        policy = DNSPolicy.model_validate(data)
        assert policy.id == "dns-3"


class TestFirewallPolicyOrderingModel:
    """Tests for FirewallPolicyOrdering model."""

    def test_create_ordering(self) -> None:
        """Test creating a firewall policy ordering from dict."""
        from unifi_official_api.network.models.firewall import FirewallPolicyOrdering

        data = {
            "orderedFirewallPolicyIds": {
                "beforeSystemDefined": ["p-1", "p-2"],
                "afterSystemDefined": ["p-3"],
            }
        }
        ordering = FirewallPolicyOrdering.model_validate(data)
        assert ordering.ordered_firewall_policy_ids.before_system_defined == [
            "p-1",
            "p-2",
        ]
        assert ordering.ordered_firewall_policy_ids.after_system_defined == ["p-3"]

    def test_ordering_empty_lists(self) -> None:
        """Test ordering with empty lists."""
        from unifi_official_api.network.models.firewall import FirewallPolicyOrdering

        data = {
            "orderedFirewallPolicyIds": {
                "beforeSystemDefined": [],
                "afterSystemDefined": [],
            }
        }
        ordering = FirewallPolicyOrdering.model_validate(data)
        assert ordering.ordered_firewall_policy_ids.before_system_defined == []
        assert ordering.ordered_firewall_policy_ids.after_system_defined == []


class TestACLRuleOrderingModel:
    """Tests for ACLRuleOrdering model."""

    def test_create_ordering(self) -> None:
        """Test creating an ACL rule ordering from dict."""
        from unifi_official_api.network.models.acl import ACLRuleOrdering

        data = {"orderedAclRuleIds": ["acl-1", "acl-2", "acl-3"]}
        ordering = ACLRuleOrdering.model_validate(data)
        assert ordering.ordered_acl_rule_ids == ["acl-1", "acl-2", "acl-3"]

    def test_ordering_empty(self) -> None:
        """Test ACL ordering with empty list."""
        from unifi_official_api.network.models.acl import ACLRuleOrdering

        data = {"orderedAclRuleIds": []}
        ordering = ACLRuleOrdering.model_validate(data)
        assert ordering.ordered_acl_rule_ids == []
