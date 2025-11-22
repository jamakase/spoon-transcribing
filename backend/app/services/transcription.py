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

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
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
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            }
            for seg in result["segments"]
        ]
    }
