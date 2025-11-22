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
        headers_primary = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        headers_alt = {
            "Authorization": self.api_key,
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

        bases = [self.base_url]
        bases.extend([
            "https://us-east-1.recall.ai/api/v1",
            "https://us-west-2.recall.ai/api/v1",
            "https://eu-central-1.recall.ai/api/v1",
            "https://ap-northeast-1.recall.ai/api/v1",
            "https://api.recall.ai/v1",
        ])

        async with aiohttp.ClientSession() as session:
            last_error = None
            for base in bases:
                try:
                    async with session.post(f"{base}/bot", json=payload, headers=headers_primary) as resp:
                        if resp.status in (401, 403):
                            async with session.post(f"{base}/bot", json=payload, headers=headers_alt) as resp2:
                                resp2.raise_for_status()
                                return await resp2.json()
                        resp.raise_for_status()
                        return await resp.json()
                except Exception as e:
                    last_error = e
                    continue
            raise last_error if last_error else RuntimeError("recall start failed")

    async def get_bot(self, bot_id: str) -> dict:
        headers_primary = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        headers_alt = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        bases = [self.base_url]
        bases.extend([
            "https://us-east-1.recall.ai/api/v1",
            "https://us-west-2.recall.ai/api/v1",
            "https://eu-central-1.recall.ai/api/v1",
            "https://ap-northeast-1.recall.ai/api/v1",
            "https://api.recall.ai/v1",
        ])
        async with aiohttp.ClientSession() as session:
            last_error = None
            for base in bases:
                try:
                    async with session.get(f"{base}/bot/{bot_id}", headers=headers_primary) as resp:
                        if resp.status in (401, 403):
                            async with session.get(f"{base}/bot/{bot_id}", headers=headers_alt) as resp2:
                                resp2.raise_for_status()
                                return await resp2.json()
                        resp.raise_for_status()
                        return await resp.json()
                except Exception as e:
                    last_error = e
                    continue
            raise last_error if last_error else RuntimeError("recall get bot failed")

    async def get_recording(self, recording_id: str) -> dict:
        headers_primary = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        headers_alt = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

        bases = [self.base_url]
        bases.extend([
            "https://us-east-1.recall.ai/api/v1",
            "https://us-west-2.recall.ai/api/v1",
            "https://eu-central-1.recall.ai/api/v1",
            "https://ap-northeast-1.recall.ai/api/v1",
            "https://api.recall.ai/v1",
        ])

        async with aiohttp.ClientSession() as session:
            last_error = None
            for base in bases:
                try:
                    async with session.get(f"{base}/recording/{recording_id}", headers=headers_primary) as resp:
                        if resp.status in (401, 403):
                            async with session.get(f"{base}/recording/{recording_id}", headers=headers_alt) as resp2:
                                resp2.raise_for_status()
                                return await resp2.json()
                        resp.raise_for_status()
                        return await resp.json()
                except Exception as e:
                    last_error = e
                    continue
            raise last_error if last_error else RuntimeError("recall get recording failed")


recall_service = RecallService()