"""Tests for UniFi Network client."""

from __future__ import annotations

from typing import Any

from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth, ConnectionType
from unifi_official_api.network import UniFiNetworkClient


class TestUniFiNetworkClient:
    """Tests for UniFiNetworkClient."""

    async def test_client_creation(self, auth: ApiKeyAuth) -> None:
        """Test client creation with default (REMOTE) connection type."""
        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            assert client.base_url.host == "api.ui.com"
            assert not client.closed

    async def test_client_close(self, auth: ApiKeyAuth) -> None:
        """Test client close."""
        client = UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        )
        assert not client.closed
        await client.close()
        assert client.closed

    async def test_client_context_manager(self, auth: ApiKeyAuth) -> None:
        """Test client as context manager."""
        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            assert not client.closed
        assert client.closed

    async def test_validate_connection(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test connection validation."""
        mock_aioresponse.get(
            "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites",
            payload={"data": []},
        )

        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            result = await client.validate_connection()
            assert result is True

    async def test_get_sites(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
    ) -> None:
        """Test getting sites."""
        mock_aioresponse.get(
            "https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites",
            payload={"data": [{"id": "site-1", "name": "Test Site"}]},
        )

        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            sites = await client.sites.get_all()
            assert len(sites) == 1
            assert sites[0].id == "site-1"

    async def test_endpoints_available(self, auth: ApiKeyAuth) -> None:
        """Test that all endpoints are available."""
        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            assert client.devices is not None
            assert client.clients is not None
            assert client.networks is not None
            assert client.wifi is not None
            assert client.sites is not None
            assert client.firewall is not None


class TestDevicesEndpoint:
    """Tests for devices endpoint."""

    async def test_list_devices(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
        site_id: str,
        sample_device: dict[str, Any],
    ) -> None:
        """Test listing devices."""
        mock_aioresponse.get(
            f"https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/{site_id}/devices",
            payload={"data": [sample_device]},
        )

        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            devices = await client.devices.get_all(site_id)
            assert len(devices) == 1
            assert devices[0].id == "device-123"
            assert devices[0].mac == "00:11:22:33:44:55"

    async def test_get_device(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
        site_id: str,
        sample_device: dict[str, Any],
    ) -> None:
        """Test getting a specific device."""
        device_id = sample_device["id"]
        mock_aioresponse.get(
            f"https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/{site_id}/devices/{device_id}",
            payload={"data": sample_device},
        )

        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            device = await client.devices.get(site_id, device_id)
            assert device.id == device_id
            assert device.name == "Test Switch"


class TestClientsEndpoint:
    """Tests for clients endpoint."""

    async def test_list_clients(
        self,
        auth: ApiKeyAuth,
        mock_aioresponse: aioresponses,
        site_id: str,
        sample_client: dict[str, Any],
    ) -> None:
        """Test listing clients."""
        mock_aioresponse.get(
            f"https://api.ui.com/v1/connector/consoles/test-console-id/proxy/network/integration/v1/sites/{site_id}/clients",
            payload={"data": [sample_client]},
        )

        async with UniFiNetworkClient(
            auth=auth,
            connection_type=ConnectionType.REMOTE,
            console_id="test-console-id",
        ) as client:
            clients = await client.clients.get_all(site_id)
            assert len(clients) == 1
            assert clients[0].id == "client-123"
            assert clients[0].display_name == "Test Device"
