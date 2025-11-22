import os
import aiohttp
from yarl import URL
import whisper

from app.config import settings

_model = None


def get_whisper_model():
    global _model
    if _model is None:
        _model = whisper.load_model(settings.whisper_model)
    return _model


async def download_audio(url: str, meeting_id: int) -> str:
    os.makedirs(settings.upload_dir, exist_ok=True)
    file_path = os.path.join(settings.upload_dir, f"meeting_{meeting_id}.audio")

    headers_primary = {}
    headers_alt = {}
    if ("recall.ai" in url or "recall.ai" in url.lower()) and settings.recall_api_key:
        headers_primary = {"Authorization": f"Token {settings.recall_api_key}"}
        headers_alt = {"Authorization": settings.recall_api_key}
    elif ("zoom.us" in url or "zoom.us" in url.lower()) and settings.zoom_access_token:
        headers_primary = {"Authorization": f"Bearer {settings.zoom_access_token}"}

    # Use encoded=True to prevent double-encoding of pre-signed S3 URLs
    request_url = URL(url, encoded=True)

    async with aiohttp.ClientSession() as session:
        async def _download(h):
            async with session.get(request_url, headers=h) as response:
                if response.status in (401, 403) and headers_alt:
                    async with session.get(request_url, headers=headers_alt) as resp2:
                        resp2.raise_for_status()
                        with open(file_path, "wb") as f:
                            async for chunk in resp2.content.iter_chunked(8192):
                                f.write(chunk)
                        return
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
        await _download(headers_primary)

    return file_path


def transcribe_audio_file(file_path: str) -> dict:
    model = get_whisper_model()
    result = model.transcribe(file_path)

    return {
        "text": result["text"],
        "segments": {
            "items": [
                {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"]
                }
                for seg in result["segments"]
            ]
        }
    }
