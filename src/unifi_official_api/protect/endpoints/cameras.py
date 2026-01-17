"""Cameras endpoint for UniFi Protect API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models import Camera, RecordingMode
from ..models.files import RTSPSStream, TalkbackSession

if TYPE_CHECKING:
    from ..client import UniFiProtectClient


class CamerasEndpoint:
    """Endpoint for managing UniFi Protect cameras."""

    def __init__(self, client: UniFiProtectClient) -> None:
        """Initialize the cameras endpoint.

        Args:
            client: The UniFi Protect client.
        """
        self._client = client

    async def get_all(self, host_id: str, site_id: str) -> list[Camera]:
        """List all cameras.

        Args:
            host_id: The host ID.
            site_id: The site ID.

        Returns:
            List of cameras.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras"
        response = await self._client._get(path)

        if response is None:
            return []

        data = response.get("data", response) if isinstance(response, dict) else response
        if isinstance(data, list):
            return [Camera.model_validate(item) for item in data]
        return []

    async def get(self, host_id: str, site_id: str, camera_id: str) -> Camera:
        """Get a specific camera.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            The camera.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Camera.model_validate(data)
            if isinstance(data, list) and len(data) > 0:
                return Camera.model_validate(data[0])
        raise ValueError(f"Camera {camera_id} not found")

    async def update(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        **kwargs: Any,
    ) -> Camera:
        """Update camera settings.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            **kwargs: Settings to update.

        Returns:
            The updated camera.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}"
        response = await self._client._patch(path, json_data=kwargs)

        if isinstance(response, dict):
            result = response.get("data", response)
            if isinstance(result, dict):
                return Camera.model_validate(result)
        raise ValueError("Failed to update camera")

    async def set_recording_mode(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        mode: RecordingMode,
    ) -> Camera:
        """Set camera recording mode.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            mode: The recording mode.

        Returns:
            The updated camera.
        """
        return await self.update(
            host_id, site_id, camera_id, recordingMode=mode.value
        )

    async def get_snapshot(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        width: int | None = None,
        height: int | None = None,
    ) -> bytes:
        """Get a snapshot from the camera.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            width: Optional width for the snapshot.
            height: Optional height for the snapshot.

        Returns:
            The snapshot image bytes.
        """
        params: dict[str, Any] = {}
        if width:
            params["w"] = width
        if height:
            params["h"] = height

        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/snapshot"
        return await self._client._get_binary(path, params=params)

    async def restart(self, host_id: str, site_id: str, camera_id: str) -> bool:
        """Restart a camera.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/restart"
        await self._client._post(path)
        return True

    async def set_microphone_volume(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        volume: int,
    ) -> Camera:
        """Set camera microphone volume.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            volume: Volume level (0-100).

        Returns:
            The updated camera.
        """
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")
        return await self.update(host_id, site_id, camera_id, micVolume=volume)

    async def set_speaker_volume(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        volume: int,
    ) -> Camera:
        """Set camera speaker volume.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            volume: Volume level (0-100).

        Returns:
            The updated camera.
        """
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100")
        return await self.update(host_id, site_id, camera_id, speakerVolume=volume)

    async def ptz_move(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        *,
        pan: float | None = None,
        tilt: float | None = None,
        zoom: float | None = None,
    ) -> bool:
        """Move PTZ camera.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            pan: Pan value (-1.0 to 1.0).
            tilt: Tilt value (-1.0 to 1.0).
            zoom: Zoom value (0.0 to 1.0).

        Returns:
            True if successful.
        """
        data: dict[str, Any] = {}
        if pan is not None:
            data["pan"] = pan
        if tilt is not None:
            data["tilt"] = tilt
        if zoom is not None:
            data["zoom"] = zoom

        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/ptz/move"
        await self._client._post(path, json_data=data)
        return True

    async def ptz_goto_preset(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        preset_id: str,
    ) -> bool:
        """Move PTZ camera to a preset position.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            preset_id: The preset position ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/ptz/goto/{preset_id}"
        await self._client._post(path)
        return True

    async def ptz_patrol_start(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        slot: int,
    ) -> bool:
        """Start PTZ patrol.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            slot: Patrol slot number (0-4).

        Returns:
            True if successful.
        """
        if not 0 <= slot <= 4:
            raise ValueError("Slot must be between 0 and 4")
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/ptz/patrol/start/{slot}"
        await self._client._post(path)
        return True

    async def ptz_patrol_stop(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
    ) -> bool:
        """Stop active PTZ patrol.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/ptz/patrol/stop"
        await self._client._post(path)
        return True

    async def create_rtsps_stream(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
    ) -> RTSPSStream:
        """Create RTSPS stream for camera.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            RTSPS stream configuration.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/rtsps-stream"
        response = await self._client._post(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return RTSPSStream.model_validate(data)
        raise ValueError("Failed to create RTSPS stream")

    async def get_rtsps_stream(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
    ) -> RTSPSStream:
        """Get RTSPS stream configuration.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            RTSPS stream configuration.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/rtsps-stream"
        response = await self._client._get(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return RTSPSStream.model_validate(data)
        raise ValueError("RTSPS stream not found")

    async def delete_rtsps_stream(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
    ) -> bool:
        """Delete RTSPS stream.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            True if successful.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/rtsps-stream"
        await self._client._delete(path)
        return True

    async def create_talkback_session(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
    ) -> TalkbackSession:
        """Create a talkback (two-way audio) session.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            Talkback session configuration with URL and audio settings.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/talkback-session"
        response = await self._client._post(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return TalkbackSession.model_validate(data)
        raise ValueError("Failed to create talkback session")

    async def disable_mic_permanently(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
    ) -> Camera:
        """Permanently disable camera microphone.

        This action cannot be undone.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.

        Returns:
            The updated camera with microphone disabled.
        """
        path = f"/ea/hosts/{host_id}/sites/{site_id}/cameras/{camera_id}/disable-mic-permanently"
        response = await self._client._post(path)

        if isinstance(response, dict):
            data = response.get("data", response)
            if isinstance(data, dict):
                return Camera.model_validate(data)
        raise ValueError("Failed to disable microphone")

    async def set_hdr_mode(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        mode: str,
    ) -> Camera:
        """Set camera HDR mode.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            mode: HDR mode (auto, on, off).

        Returns:
            The updated camera.
        """
        if mode not in ("auto", "on", "off"):
            raise ValueError("HDR mode must be 'auto', 'on', or 'off'")
        return await self.update(host_id, site_id, camera_id, hdrType=mode)

    async def set_video_mode(
        self,
        host_id: str,
        site_id: str,
        camera_id: str,
        mode: str,
    ) -> Camera:
        """Set camera video mode.

        Args:
            host_id: The host ID.
            site_id: The site ID.
            camera_id: The camera ID.
            mode: Video mode (default, highFps, sport, slowShutter, etc).

        Returns:
            The updated camera.
        """
        return await self.update(host_id, site_id, camera_id, videoMode=mode)
