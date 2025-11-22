import aiohttp
from app.config import settings


class RecallService:
    def __init__(self):
        if settings.recall_base_url:
            self.base_url = settings.recall_base_url.rstrip("/")
        else:
            region = settings.recall_region or "us-east-1"
            self.base_url = f"https://{region}.recall.ai/api/v1"
        self.api_key = settings.recall_api_key

    async def start_bot(self, meeting_url: str, bot_name: str | None = None, external_id: str | None = None) -> dict:
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "meeting_url": meeting_url,
            "recording_config": {
                "video_mixed_mp4": {},
            },
        }
        if bot_name:
            payload["bot_name"] = bot_name
        if external_id:
            payload["external_id"] = external_id
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/bot", json=payload, headers=headers) as resp:
                if resp.status == 401:
                    # Fallback: try without Token prefix
                    headers["Authorization"] = self.api_key
                    async with session.post(f"{self.base_url}/bot", json=payload, headers=headers) as resp2:
                        resp2.raise_for_status()
                        return await resp2.json()
                resp.raise_for_status()
                return await resp.json()


recall_service = RecallService()