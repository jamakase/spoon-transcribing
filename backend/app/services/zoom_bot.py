"""Zoom bot service for joining meetings and streaming audio."""

import logging
from datetime import datetime, timedelta
from typing import Optional
import base64
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
        """Get a valid Zoom API access token using Server-to-Server OAuth."""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            logger.info("🔓 Using cached Zoom access token")
            return self._access_token

        logger.info("🔑 Requesting new Zoom access token via Server-to-Server OAuth...")

        if not settings.zoom_client_id or not settings.zoom_client_secret or not settings.zoom_account_id:
            raise RuntimeError("Zoom server-to-server OAuth not configured: set ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_ACCOUNT_ID")

        auth = base64.b64encode(f"{settings.zoom_client_id}:{settings.zoom_client_secret}".encode()).decode()
        token_url = "https://zoom.us/oauth/token"
        params = {
            "grant_type": "account_credentials",
            "account_id": settings.zoom_account_id,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, params=params, headers={"Authorization": f"Basic {auth}"}) as resp:
                logger.info(f"   OAuth response status: {resp.status}")
                if resp.status != 200:
                    text = await resp.text()
                    logger.error(f"❌ Failed to get Zoom access token: {text}")
                    raise RuntimeError(f"Zoom token error: {text}")
                data = await resp.json()
                self._access_token = data["access_token"]
                self._token_expires_at = now + timedelta(seconds=data.get("expires_in", self.TOKEN_EXPIRY))
                logger.info(f"✅ New access token obtained, expires in {data.get('expires_in', self.TOKEN_EXPIRY)} seconds")
                return self._access_token

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


zoom_bot_service = ZoomBotService()
