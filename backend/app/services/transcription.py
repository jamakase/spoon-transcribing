import os
import aiohttp
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

    headers = {}
    if ("zoom.us" in url or "zoom.us" in url.lower()) and settings.zoom_access_token:
        headers["Authorization"] = f"Bearer {settings.zoom_access_token}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            with open(file_path, "wb") as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)

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
