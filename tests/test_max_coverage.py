"""Comprehensive edge-case and branch coverage tests."""

from __future__ import annotations

import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth, ConnectionType, LocalAuth
from unifi_official_api.network import UniFiNetworkClient
from unifi_official_api.protect import UniFiProtectClient


class TestMaxCoverage:
    """Tests for edge cases across all modules to reach >98% coverage."""

    @pytest.fixture
    def net_client(self) -> UniFiNetworkClient:
        return UniFiNetworkClient(
            auth=LocalAuth(api_key="key", verify_ssl=False),
            base_url="https://192.168.1.1",
            connection_type=ConnectionType.LOCAL,
        )

    @pytest.fixture
    def net_remote_client(self) -> UniFiNetworkClient:
        return UniFiNetworkClient(
            auth=ApiKeyAuth(api_key="key"),
            connection_type=ConnectionType.REMOTE,
            console_id="console-123",
        )

    @pytest.fixture
    def prot_client(self) -> UniFiProtectClient:
        return UniFiProtectClient(
            auth=LocalAuth(api_key="key", verify_ssl=False),
            base_url="https://192.168.1.1",
            connection_type=ConnectionType.LOCAL,
        )

    @pytest.fixture
    def prot_remote_client(self) -> UniFiProtectClient:
        return UniFiProtectClient(
            auth=ApiKeyAuth(api_key="key"),
            connection_type=ConnectionType.REMOTE,
            console_id="console-123",
        )

    async def test_network_client_branches(
        self,
        net_client: UniFiNetworkClient,
        net_remote_client: UniFiNetworkClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test network client remote paths and edge cases."""
        assert (
            net_remote_client.build_api_path("/sites")
            == "/v1/connector/consoles/console-123/network/integration/v1/sites"
        )
        assert net_remote_client.console_id == "console-123"

        mock_aioresponse.get(
            "https://192.168.1.1/proxy/network/integration/v1/sites?filter=name%3DDefault",
            payload={"data": [{"id": "default", "name": "Default", "isOwner": True}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/network/integration/v1/sites/default/devices/dev-1/statistics/latest",
            payload={"data": {"cpu": 15.2, "memory": 45.0}},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/network/api/self/sites",
            payload={"data": [{"name": "default"}]},
        )

        async with net_client:
            sites = await net_client.sites.get_all(filter_str="name=Default")
            assert len(sites) == 1

            legacy_sites = await net_client.sites.get_legacy_all()
            assert len(legacy_sites) == 1

            stats = await net_client.devices.get_statistics("default", "dev-1")
            assert stats.get("cpu") == 15.2

    async def test_protect_client_extended_branches(
        self,
        prot_client: UniFiProtectClient,
        prot_remote_client: UniFiProtectClient,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test protect client and endpoint branches."""
        assert (
            prot_remote_client.build_api_path("/cameras")
            == "/v1/connector/consoles/console-123/protect/integration/v1/cameras"
        )

        # Protect list single object unwrapping
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/alarm-hubs/hub-1",
            payload={"data": [{"id": "hub-1", "name": "Hub List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/bridges/bridge-1",
            payload={"data": [{"id": "bridge-1", "name": "Bridge List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/link-stations/station-1",
            payload={"data": [{"id": "station-1", "name": "Station List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/speakers/spk-1",
            payload={"data": [{"id": "spk-1", "name": "Speaker List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/sirens/siren-1",
            payload={"data": [{"id": "siren-1", "name": "Siren List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/fobs/fob-1",
            payload={"data": [{"id": "fob-1", "name": "Fob List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/relays/relay-1",
            payload={"data": [{"id": "relay-1", "name": "Relay List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/users/u-1",
            payload={"data": [{"id": "u-1", "name": "User List Item"}]},
        )
        mock_aioresponse.get(
            "https://192.168.1.1/proxy/protect/integration/v1/ulp-users/ulp-1",
            payload={
                "data": [
                    {
                        "id": "ulp-1",
                        "firstName": "A",
                        "lastName": "B",
                        "fullName": "A B",
                        "status": "ACTIVE",
                    }
                ]
            },
        )

        async with prot_client:
            hub = await prot_client.alarm_hubs.get("hub-1")
            assert hub.id == "hub-1"

            br = await prot_client.bridges.get("bridge-1")
            assert br.id == "bridge-1"

            ls = await prot_client.link_stations.get("station-1")
            assert ls.id == "station-1"

            spk = await prot_client.speakers.get("spk-1")
            assert spk.id == "spk-1"

            sr = await prot_client.sirens.get("siren-1")
            assert sr.id == "siren-1"

            fb = await prot_client.fobs.get("fob-1")
            assert fb.id == "fob-1"

            rl = await prot_client.relays.get("relay-1")
            assert rl.id == "relay-1"

            u = await prot_client.users.get_user("u-1")
            assert u.id == "u-1"

            ulp = await prot_client.users.get_ulp_user("ulp-1")
            assert ulp.id == "ulp-1"
