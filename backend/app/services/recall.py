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
            "bot_name": bot_name or "wiped.os",
            "recording_config": {
                "video_mixed_mp4": {},
                "audio_mixed_mp3": {},
            },
        }
        # Set bot image if configured
        bot_image_url = getattr(settings, 'recall_bot_image_url', None)
        if bot_image_url:
            payload["bot_image"] = bot_image_url
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

    async def get_audio_mixed(self, recording_id: str) -> dict:
        """Get audio mixed data - this is a placeholder that returns empty since
        Recall API doesn't have this endpoint. Use get_bot() to get media_shortcuts instead."""
        return {}

    async def get_bot_audio_url(self, bot_id: str) -> str | None:
        """Get the audio download URL from a bot's recordings via media_shortcuts."""
        try:
            bot_data = await self.get_bot(bot_id)
            recordings = bot_data.get("recordings") or []
            for rec in recordings:
                # Try media_shortcuts first (correct Recall API structure)
                ms = rec.get("media_shortcuts") or {}
                for key in ("audio_mixed", "audio_mixed_mp3", "video_mixed", "video_mixed_mp4"):
                    obj = ms.get(key)
                    if isinstance(obj, dict):
                        data = obj.get("data") or {}
                        dl = data.get("download_url")
                        if dl:
                            return dl
                # Fallback to direct download_url
                url = rec.get("download_url") or rec.get("audio_url") or rec.get("url")
                if url:
                    return url
            return None
        except Exception:
            return None


recall_service = RecallService()