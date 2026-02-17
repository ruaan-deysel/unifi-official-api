"""Firewall endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import FirewallRule, FirewallZone
from ..models.firewall import FirewallPolicyOrdering

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class FirewallEndpoint:
    """Endpoint for managing firewall rules and zones."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the firewall endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def list_zones(self, site_id: str) -> list[FirewallZone]:
        """List all firewall zones.

        Args:
            site_id: The site ID.

        Returns:
            List of firewall zones.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/zones")
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [FirewallZone.model_validate(item) for item in data]
        return []

    async def get_zone(self, site_id: str, zone_id: str) -> FirewallZone:
        """Get a specific firewall zone.

        Args:
            site_id: The site ID.
            zone_id: The firewall zone ID.

        Returns:
            The firewall zone.

        Raises:
            ValueError: If the zone is not found.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/zones/{zone_id}")
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return FirewallZone.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return FirewallZone.model_validate(data[0])
        raise ValueError(f"Firewall zone {zone_id} not found")

    async def create_zone(
        self,
        site_id: str,
        *,
        name: str,
        network_ids: list[str] | None = None,
        **kwargs: Any,
    ) -> FirewallZone:
        """Create a new custom firewall zone.

        Args:
            site_id: The site ID.
            name: Name of the firewall zone.
            network_ids: List of network IDs to attach to the zone.
            **kwargs: Additional parameters.

        Returns:
            The created firewall zone.

        Raises:
            ValueError: If the zone creation fails.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/zones")
        data: dict[str, Any] = {
            "name": name,
            "networkIds": network_ids or [],
        }
        data.update(kwargs)

        response = await self._client._post(path, json_data=data)
        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return FirewallZone.model_validate(result)
        raise ValueError("Failed to create firewall zone")

    async def update_zone(
        self,
        site_id: str,
        zone_id: str,
        *,
        name: str,
        network_ids: list[str],
        **kwargs: Any,
    ) -> FirewallZone:
        """Update a firewall zone.

        Args:
            site_id: The site ID.
            zone_id: The firewall zone ID.
            name: Name of the firewall zone.
            network_ids: List of network IDs to attach to the zone.
            **kwargs: Additional parameters.

        Returns:
            The updated firewall zone.

        Raises:
            ValueError: If the zone update fails.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/zones/{zone_id}")
        data: dict[str, Any] = {
            "name": name,
            "networkIds": network_ids,
        }
        data.update(kwargs)

        response = await self._client._put(path, json_data=data)
        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return FirewallZone.model_validate(result)
        raise ValueError("Failed to update firewall zone")

    async def delete_zone(self, site_id: str, zone_id: str) -> bool:
        """Delete a custom firewall zone.

        Only user-defined (custom) zones can be deleted.

        Args:
            site_id: The site ID.
            zone_id: The firewall zone ID.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/zones/{zone_id}")
        await self._client._delete(path)
        return True

    async def list_rules(self, site_id: str) -> list[FirewallRule]:
        """List all firewall rules.

        Args:
            site_id: The site ID.

        Returns:
            List of firewall rules.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies")
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [FirewallRule.model_validate(item) for item in data]
        return []

    async def get_rule(self, site_id: str, rule_id: str) -> FirewallRule:
        """Get a specific firewall rule.

        Args:
            site_id: The site ID.
            rule_id: The rule ID.

        Returns:
            The firewall rule.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies/{rule_id}")
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return FirewallRule.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return FirewallRule.model_validate(data[0])
        raise ValueError(f"Firewall rule {rule_id} not found")

    async def create_rule(
        self,
        site_id: str,
        *,
        name: str,
        action: str = "drop",
        protocol: str = "all",
        source_zone_id: str | None = None,
        destination_zone_id: str | None = None,
        **kwargs: Any,
    ) -> FirewallRule:
        """Create a new firewall rule.

        Args:
            site_id: The site ID.
            name: Rule name.
            action: Rule action (accept, drop, reject).
            protocol: Protocol to match.
            source_zone_id: Source zone ID.
            destination_zone_id: Destination zone ID.
            **kwargs: Additional parameters.

        Returns:
            The created firewall rule.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies")
        data: dict[str, Any] = {
            "name": name,
            "action": action,
            "protocol": protocol,
        }
        if source_zone_id is not None:
            data["sourceZoneId"] = source_zone_id
        if destination_zone_id is not None:
            data["destinationZoneId"] = destination_zone_id
        data.update(kwargs)

        response = await self._client._post(path, json_data=data)
        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return FirewallRule.model_validate(result)
        raise ValueError("Failed to create firewall rule")

    async def update_rule(
        self,
        site_id: str,
        rule_id: str,
        **kwargs: Any,
    ) -> FirewallRule:
        """Update a firewall rule.

        Args:
            site_id: The site ID.
            rule_id: The rule ID.
            **kwargs: Parameters to update.

        Returns:
            The updated firewall rule.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies/{rule_id}")
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return FirewallRule.model_validate(result)
        raise ValueError("Failed to update firewall rule")

    async def patch_rule(
        self,
        site_id: str,
        rule_id: str,
        **kwargs: Any,
    ) -> FirewallRule:
        """Partially update a firewall policy.

        Unlike update_rule which replaces the entire policy, patch_rule
        allows updating individual fields without sending the full object.

        Args:
            site_id: The site ID.
            rule_id: The rule ID.
            **kwargs: Parameters to patch (e.g., loggingEnabled=True).

        Returns:
            The patched firewall rule.

        Raises:
            ValueError: If the patch fails.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies/{rule_id}")
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return FirewallRule.model_validate(result)
        raise ValueError("Failed to patch firewall rule")

    async def delete_rule(self, site_id: str, rule_id: str) -> bool:
        """Delete a firewall rule.

        Args:
            site_id: The site ID.
            rule_id: The rule ID.

        Returns:
            True if successful.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies/{rule_id}")
        await self._client._delete(path)
        return True

    async def get_policy_ordering(
        self,
        site_id: str,
        *,
        source_zone_id: str,
        destination_zone_id: str,
    ) -> FirewallPolicyOrdering:
        """Get user-defined firewall policy ordering for a zone pair.

        Args:
            site_id: The site ID.
            source_zone_id: The source firewall zone ID.
            destination_zone_id: The destination firewall zone ID.

        Returns:
            The firewall policy ordering.

        Raises:
            ValueError: If the ordering cannot be retrieved.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies/ordering")
        params: dict[str, Any] = {
            "sourceFirewallZoneId": source_zone_id,
            "destinationFirewallZoneId": destination_zone_id,
        }
        response = await self._client._get(path, params=params)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return FirewallPolicyOrdering.model_validate(data)
        raise ValueError("Failed to get firewall policy ordering")

    async def update_policy_ordering(
        self,
        site_id: str,
        *,
        source_zone_id: str,
        destination_zone_id: str,
        before_system_defined: list[str] | None = None,
        after_system_defined: list[str] | None = None,
    ) -> FirewallPolicyOrdering:
        """Reorder user-defined firewall policies for a zone pair.

        Args:
            site_id: The site ID.
            source_zone_id: The source firewall zone ID.
            destination_zone_id: The destination firewall zone ID.
            before_system_defined: Policy IDs to place before system-defined rules.
            after_system_defined: Policy IDs to place after system-defined rules.

        Returns:
            The updated firewall policy ordering.

        Raises:
            ValueError: If the reordering fails.
        """
        path = self._client.build_api_path(f"/sites/{site_id}/firewall/policies/ordering")
        params: dict[str, Any] = {
            "sourceFirewallZoneId": source_zone_id,
            "destinationFirewallZoneId": destination_zone_id,
        }
        data: dict[str, Any] = {
            "orderedFirewallPolicyIds": {
                "beforeSystemDefined": before_system_defined or [],
                "afterSystemDefined": after_system_defined or [],
            }
        }
        response = await self._client._put(path, json_data=data, params=params)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return FirewallPolicyOrdering.model_validate(result)
        raise ValueError("Failed to update firewall policy ordering")
