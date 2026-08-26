"""Tests for UniFi Carrier Fabric client and endpoints."""

from __future__ import annotations

import pytest
from aioresponses import aioresponses

from unifi_official_api import ApiKeyAuth
from unifi_official_api.carrier_fabric import (
    HostLinkResponse,
    ServicePlan,
    Subscriber,
    SubscriberCreate,
    SubscriberListResponse,
    SubscriberPatch,
    UniFiCarrierFabricClient,
)


class TestUniFiCarrierFabricClient:
    """Tests for UniFiCarrierFabricClient."""

    @pytest.fixture
    def client(self) -> UniFiCarrierFabricClient:
        """Create Carrier Fabric client."""
        return UniFiCarrierFabricClient(
            auth=ApiKeyAuth(api_key="cloud-api-key"),
        )

    async def test_subscribers_crud(
        self, client: UniFiCarrierFabricClient, mock_aioresponse: aioresponses
    ) -> None:
        """Test subscriber CRUD operations."""
        mock_aioresponse.get(
            "https://api.ui.com/v1/carrier/subscribers?cursor=cur-1&limit=50&search=Acme&state=provisioned",
            payload={
                "data": [
                    {
                        "id": "sub-1",
                        "subscriberNumber": "SUB-1001",
                        "name": "Acme Corp",
                        "state": "provisioned",
                        "suspended": False,
                    }
                ],
                "meta": {"limit": 50, "hasMore": False},
            },
        )
        mock_aioresponse.get("https://api.ui.com/v1/carrier/subscribers?limit=10", payload=None)
        mock_aioresponse.post(
            "https://api.ui.com/v1/carrier/subscribers",
            payload={
                "data": {
                    "id": "sub-2",
                    "subscriberNumber": "SUB-1002",
                    "name": "Beta LLC",
                    "state": "pending_assignment",
                    "suspended": False,
                }
            },
        )
        mock_aioresponse.post(
            "https://api.ui.com/v1/carrier/subscribers",
            payload={"data": {"id": "sub-3", "subscriberNumber": "SUB-1003"}},
        )
        mock_aioresponse.post("https://api.ui.com/v1/carrier/subscribers", payload={})
        mock_aioresponse.get(
            "https://api.ui.com/v1/carrier/subscribers/sub-1",
            payload={
                "data": {
                    "id": "sub-1",
                    "subscriberNumber": "SUB-1001",
                    "name": "Acme Corp",
                    "state": "provisioned",
                    "suspended": False,
                }
            },
        )
        mock_aioresponse.get("https://api.ui.com/v1/carrier/subscribers/bad-id", payload={})
        mock_aioresponse.patch(
            "https://api.ui.com/v1/carrier/subscribers/sub-1",
            payload={
                "data": {
                    "id": "sub-1",
                    "subscriberNumber": "SUB-1001",
                    "name": "Acme Corporation",
                    "state": "provisioned",
                    "suspended": False,
                }
            },
        )
        mock_aioresponse.patch(
            "https://api.ui.com/v1/carrier/subscribers/sub-1",
            payload={"data": {"id": "sub-1", "name": "Acme LLC"}},
        )
        mock_aioresponse.patch("https://api.ui.com/v1/carrier/subscribers/bad-id", payload={})

        async with client:
            subs = await client.subscribers.get_all(
                cursor="cur-1", search="Acme", state="provisioned"
            )
            assert isinstance(subs, SubscriberListResponse)
            assert len(subs.data) == 1
            assert subs.data[0].subscriber_number == "SUB-1001"

            empty_subs = await client.subscribers.get_all(limit=10)
            assert empty_subs.data == []

            created = await client.subscribers.create(
                SubscriberCreate(subscriber_number="SUB-1002", name="Beta LLC")
            )
            assert isinstance(created, Subscriber)
            assert created.id == "sub-2"

            created_dict = await client.subscribers.create({"subscriberNumber": "SUB-1003"})
            assert created_dict.id == "sub-3"

            with pytest.raises(ValueError, match="Failed to create subscriber"):
                await client.subscribers.create({"subscriberNumber": "BAD"})

            sub = await client.subscribers.get("sub-1")
            assert sub.name == "Acme Corp"

            with pytest.raises(ValueError, match="Subscriber bad-id not found"):
                await client.subscribers.get("bad-id")

            updated = await client.subscribers.update(
                "sub-1",
                SubscriberPatch(name="Acme Corporation"),
            )
            assert updated.name == "Acme Corporation"

            updated_dict = await client.subscribers.update("sub-1", {"name": "Acme LLC"})
            assert updated_dict.name == "Acme LLC"

            with pytest.raises(ValueError, match="Failed to update subscriber"):
                await client.subscribers.update("bad-id", {})

    async def test_subscriber_actions(
        self, client: UniFiCarrierFabricClient, mock_aioresponse: aioresponses
    ) -> None:
        """Test subscriber host link, plan assignment, suspend, resume."""
        mock_aioresponse.put(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/host",
            payload={"data": {"id": "sub-1", "hostId": "host-99"}, "prevHostId": None},
        )
        mock_aioresponse.put("https://api.ui.com/v1/carrier/subscribers/sub-1/host", payload=None)
        mock_aioresponse.delete(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/host",
            payload={"data": {"id": "sub-1", "hostId": None}, "prevHostId": "host-99"},
        )
        mock_aioresponse.delete(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/host", payload=None
        )
        mock_aioresponse.put(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/plan",
            payload={"data": {"id": "sub-1", "planId": "plan-1"}},
        )
        mock_aioresponse.put("https://api.ui.com/v1/carrier/subscribers/sub-1/plan", payload={})
        mock_aioresponse.post(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/suspend",
            payload={"data": {"id": "sub-1", "suspended": True, "state": "suspended"}},
        )
        mock_aioresponse.post(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/suspend",
            payload={"data": {"id": "sub-1", "suspended": True, "state": "suspended"}},
        )
        mock_aioresponse.post("https://api.ui.com/v1/carrier/subscribers/sub-1/suspend", payload={})
        mock_aioresponse.post(
            "https://api.ui.com/v1/carrier/subscribers/sub-1/resume",
            payload={"data": {"id": "sub-1", "suspended": False, "state": "installed"}},
        )
        mock_aioresponse.post("https://api.ui.com/v1/carrier/subscribers/sub-1/resume", payload={})

        async with client:
            attach_res = await client.subscribers.attach_host("sub-1", "host-99")
            assert isinstance(attach_res, HostLinkResponse)
            assert attach_res.data is not None
            assert attach_res.data.host_id == "host-99"

            empty_attach = await client.subscribers.attach_host("sub-1", "host-99")
            assert empty_attach.data is None

            detach_res = await client.subscribers.detach_host("sub-1")
            assert detach_res.prev_host_id == "host-99"

            empty_detach = await client.subscribers.detach_host("sub-1")
            assert empty_detach.data is None

            plan_res = await client.subscribers.assign_plan("sub-1", "plan-1")
            assert plan_res.plan_id == "plan-1"

            with pytest.raises(ValueError, match="Failed to assign plan"):
                await client.subscribers.assign_plan("sub-1", "plan-bad")

            susp = await client.subscribers.suspend("sub-1", reason="Billing overdue")
            assert susp.suspended is True

            susp_no_reason = await client.subscribers.suspend("sub-1")
            assert susp_no_reason.suspended is True

            with pytest.raises(ValueError, match="Failed to suspend"):
                await client.subscribers.suspend("sub-1")

            res = await client.subscribers.resume("sub-1")
            assert res.suspended is False

            with pytest.raises(ValueError, match="Failed to resume"):
                await client.subscribers.resume("sub-1")

    async def test_service_plans_endpoints(
        self, client: UniFiCarrierFabricClient, mock_aioresponse: aioresponses
    ) -> None:
        """Test service plans endpoints."""
        mock_aioresponse.get(
            "https://api.ui.com/v1/carrier/service-plans?status=active",
            payload={
                "data": [
                    {
                        "id": "plan-1",
                        "name": "Gigabit Pro",
                        "downloadMbps": 1000,
                        "uploadMbps": 1000,
                        "status": "active",
                    }
                ]
            },
        )
        mock_aioresponse.get("https://api.ui.com/v1/carrier/service-plans", payload=None)
        mock_aioresponse.get(
            "https://api.ui.com/v1/carrier/service-plans/plan-1",
            payload={
                "data": {
                    "id": "plan-1",
                    "name": "Gigabit Pro",
                    "downloadMbps": 1000,
                    "uploadMbps": 1000,
                    "status": "active",
                }
            },
        )
        mock_aioresponse.get("https://api.ui.com/v1/carrier/service-plans/bad-id", payload={})

        async with client:
            plans = await client.service_plans.get_all(status="active")
            assert len(plans) == 1
            assert isinstance(plans[0], ServicePlan)
            assert plans[0].name == "Gigabit Pro"

            empty_plans = await client.service_plans.get_all()
            assert empty_plans == []

            plan = await client.service_plans.get("plan-1")
            assert plan.download_mbps == 1000

            with pytest.raises(ValueError, match="Service plan bad-id not found"):
                await client.service_plans.get("bad-id")

    async def test_validate_connection(
        self, client: UniFiCarrierFabricClient, mock_aioresponse: aioresponses
    ) -> None:
        """Test validate_connection."""
        mock_aioresponse.get("https://api.ui.com/v1/carrier/service-plans", payload={"data": []})
        async with client:
            assert await client.validate_connection() is True
