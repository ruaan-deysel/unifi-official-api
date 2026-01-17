"""ACL Rules endpoint for UniFi Network API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.acl import ACLAction, ACLRule, ACLRuleType

if TYPE_CHECKING:
    from ..client import UniFiNetworkClient


class ACLEndpoint:
    """Endpoint for managing ACL (Access Control List) rules."""

    def __init__(self, client: UniFiNetworkClient) -> None:
        """Initialize the ACL endpoint.

        Args:
            client: The UniFi Network client.
        """
        self._client = client

    async def get_all(
        self,
        host_id: str,
        site_id: str,
        *,
        offset: int = 0,
        limit: int = 25,
        filter_query: str | None = None,
    ) -> list[ACLRule]:
        """List all ACL rules.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            offset: Pagination offset.
            limit: Maximum results (max 200).
            filter_query: Optional filter query string.

        Returns:
            List of ACL rules.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/acl-rules"
        params: dict[str, Any] = {"offset": offset, "limit": min(limit, 200)}
        if filter_query:
            params["filter"] = filter_query

        response = await self._client._get(path, params=params)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [ACLRule.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, rule_id: str) -> ACLRule:
        """Get a specific ACL rule.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            rule_id: The ACL rule ID.

        Returns:
            The ACL rule.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/acl-rules/{rule_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return ACLRule.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return ACLRule.model_validate(data[0])
        raise ValueError(f"ACL rule {rule_id} not found")

    async def create(
        self,
        host_id: str,
        site_id: str,
        *,
        name: str,
        rule_type: ACLRuleType = ACLRuleType.IPV4,
        action: ACLAction = ACLAction.BLOCK,
        index: int = 0,
        enabled: bool = True,
        description: str | None = None,
        **kwargs: Any,
    ) -> ACLRule:
        """Create a new ACL rule.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            name: Rule name.
            rule_type: Rule type (IPV4 or MAC).
            action: Allow or block action.
            index: Priority index (lower = higher priority).
            enabled: Whether rule is active.
            description: Optional description.
            **kwargs: Additional parameters (sourceFilter, destinationFilter, etc).

        Returns:
            The created ACL rule.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/acl-rules"
        data: dict[str, Any] = {
            "type": rule_type.value,
            "name": name,
            "action": action.value,
            "index": index,
            "enabled": enabled,
        }
        if description:
            data["description"] = description
        data.update(kwargs)

        response = await self._client._post(path, json_data=data)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return ACLRule.model_validate(result)
        raise ValueError("Failed to create ACL rule")

    async def update(
        self,
        host_id: str,
        site_id: str,
        rule_id: str,
        **kwargs: Any,
    ) -> ACLRule:
        """Update an ACL rule.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            rule_id: The ACL rule ID.
            **kwargs: Parameters to update.

        Returns:
            The updated ACL rule.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/acl-rules/{rule_id}"
        response = await self._client._put(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return ACLRule.model_validate(result)
        raise ValueError("Failed to update ACL rule")

    async def delete(self, host_id: str, site_id: str, rule_id: str) -> bool:
        """Delete an ACL rule.

        Only user-defined rules can be deleted.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            rule_id: The ACL rule ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/acl-rules/{rule_id}"
        await self._client._delete(path)
        return True
