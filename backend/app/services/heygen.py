import aiohttp
from app.config import settings


class HeyGenService:
    def __init__(self):
        self.base_url = "https://api.heygen.com/v2"
        self.api_key = settings.heygen_api_key

    async def list_avatars(self) -> dict:
        """List all available avatars (digital twins)."""
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/avatars", headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()


heygen_service = HeyGenService()
