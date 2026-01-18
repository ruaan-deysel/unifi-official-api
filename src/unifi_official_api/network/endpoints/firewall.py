"""Firewall endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import FirewallRule, FirewallZone

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
