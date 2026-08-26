"""Project endpoint for UniFi InnerSpace API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.project import ProjectData

if TYPE_CHECKING:
    from ..client import UniFiInnerSpaceClient


class ProjectEndpoint:
    """Endpoint for retrieving UniFi InnerSpace project layout and shapes."""

    def __init__(self, client: UniFiInnerSpaceClient) -> None:
        self._client = client

    async def get(self) -> ProjectData:
        path = self._client.build_api_path("/project")
        response = await self._client._get(path)
        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict) and "project" in data:
                return ProjectData.model_validate(data)
        raise ValueError("Failed to retrieve InnerSpace project data")
