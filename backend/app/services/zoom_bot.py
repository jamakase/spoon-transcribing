"""Zoom bot service for joining meetings and streaming audio."""

import logging
from datetime import datetime, timedelta
from typing import Optional
import aiohttp

from app.config import settings

logger = logging.getLogger(__name__)


class ZoomBotService:
    """Service for managing Zoom bot connections and real-time transcription."""

    BASE_URL = "https://api.zoom.us/v2"
    TOKEN_EXPIRY = 3600  # 1 hour

    def __init__(self):
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    async def get_access_token(self) -> str:
        """Get a valid Zoom API access token from OAuth."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            logger.info("🔓 Using cached Zoom access token")
            return self._access_token

        # Use the OAuth access token from user authorization
        if not settings.zoom_access_token:
            raise RuntimeError("ZOOM_ACCESS_TOKEN not configured. User must authorize via OAuth first at /zoom/oauth/authorize")

        logger.info("🔐 Using OAuth access token from user authorization")
        self._access_token = settings.zoom_access_token
        self._token_expires_at = now + timedelta(seconds=self.TOKEN_EXPIRY)
        return self._access_token

    async def start_meeting_recording(self, meeting_uuid: str) -> dict:
        """Start recording for a Zoom meeting.

        Args:
            meeting_uuid: Zoom meeting UUID

        Returns:
            Response data from Zoom API
        """
        token = await self.get_access_token()
        logger.info(f"🔐 Got Zoom access token: {token[:20]}...")

        payload = {
            "action": "start",
        }

        logger.info(f"📤 Sending recording start request to Zoom API...")
        logger.info(f"   Meeting UUID: {meeting_uuid}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.patch(
                    f"{self.BASE_URL}/meetings/{meeting_uuid}/recordings/status",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"},
                ) as response:
                    logger.info(f"📥 Zoom API response status: {response.status}")
                    if response.status >= 400:
                        text = await response.text()
                        logger.error(f"❌ Zoom API error: {text}")
                        raise RuntimeError(f"Zoom API error: {text}")
                    data = await response.json()
                    logger.info(f"✅ Recording started: {data}")
                    return data
            except Exception as e:
                logger.error(f"❌ Zoom API error: {str(e)}", exc_info=True)
                raise

    async def start_meeting_bot(
        self, meeting_id: str, meeting_uuid: str, bot_jid: str
    ) -> dict:
        """Attempt to start a bot instance for a specific Zoom meeting.

        Note: Actual audio capture requires a Meeting SDK or Zoom Apps client.
        This method calls the meeting status endpoint, which may be limited.
        """
        token = await self.get_access_token()

        if not bot_jid:
            raise RuntimeError("ZOOM_BOT_JID not configured")

        payload = {
            "action": "start",
            "raw_data": {
                "jid": bot_jid,
            },
        }

        async with aiohttp.ClientSession() as session:
            async def _patch(url, json):
                return await session.patch(url, json=json, headers={"Authorization": f"Bearer {token}"})

            resp = await _patch(f"{self.BASE_URL}/meetings/{meeting_uuid}/status", payload)
            logger.info(f"📥 Zoom API response status: {resp.status}")
            text = await resp.text()
            if resp.status >= 400:
                logger.error(f"❌ Zoom API error: {text}")
                raise RuntimeError(text)
            try:
                data = await resp.json()
            except Exception:
                data = {"raw": text}
            logger.info("✅ Bot start call completed")
            return data

    async def get_meeting_info(self, meeting_id: str) -> dict:
        token = await self.get_access_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/meetings/{meeting_id}", headers={"Authorization": f"Bearer {token}"}) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def get_meeting_participants(self, meeting_id: str) -> list:
        token = await self.get_access_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/meetings/{meeting_id}/participants",
                params={"page_size": 300},
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("participants", [])

    async def get_user_zak(self, user_id: str = "me") -> str:
        token = await self.get_access_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/users/{user_id}/token",
                params={"type": "zak"},
                headers={"Authorization": f"Bearer {token}"},
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                zak = data.get("token") or data.get("zak")
                if not zak:
                    raise RuntimeError("No ZAK token returned")
                return zak


zoom_bot_service = ZoomBotService()
