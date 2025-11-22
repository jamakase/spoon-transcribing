from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json
import redis

from app.database import get_db
from app.config import settings
from app.models.meeting import Meeting
from app.tasks.transcription import transcribe_audio_task, transcribe_audio_from_url_task
from app.services.recall import recall_service
from app.services.transcription import download_audio


router = APIRouter()


 


@router.post("/webhook")
async def recall_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    meeting_id = (
        payload.get("external_id")
        or (payload.get("metadata") or {}).get("meeting_id")
        or payload.get("meeting_id")
    )

    event = payload.get("event")
    data_obj = payload.get("data") or {}
    bot_info = data_obj.get("bot") or payload.get("bot") or {}
    recording_info = data_obj.get("recording") or payload.get("recording") or {}
    bot_id = (bot_info or {}).get("id")
    recording_id = (recording_info or {}).get("id")

    if not meeting_id and bot_id:
        try:
            r = redis.Redis.from_url(settings.redis_url)
            mapped = r.get(f"recall:bot:{bot_id}")
            if mapped:
                meeting_id = mapped.decode("utf-8")
        except Exception:
            pass
    if not meeting_id and bot_id:
        try:
            bot_data = await recall_service.get_bot(str(bot_id))
            meeting_id = (
                bot_data.get("external_id")
                or (bot_data.get("metadata") or {}).get("meeting_id")
            )
        except Exception:
            pass
    if not meeting_id:
        return {"status": "ignored"}

    try:
        meeting_id_int = int(str(meeting_id))
    except Exception:
        return {"status": "ignored"}

    audio_url = None
    recordings = payload.get("recordings") or []
    def _extract_download_url(rec: dict) -> str | None:
        url = rec.get("download_url") or rec.get("audio_url") or rec.get("url")
        if url:
            return url
        ms = rec.get("media_shortcuts") or {}
        for key in ("audio_mixed", "video_mixed"):
            obj = ms.get(key)
            if isinstance(obj, dict):
                data = obj.get("data") or {}
                dl = data.get("download_url")
                if dl:
                    return dl
        return None
    if isinstance(recordings, list):
        for r in recordings:
            url = _extract_download_url(r)
            if url:
                audio_url = url
                break
    if not audio_url:
        audio_url = payload.get("audio_url") or payload.get("download_url")

    if not audio_url:
        if recording_id:
            try:
                rec_data = await recall_service.get_recording(str(recording_id))
                url = _extract_download_url(rec_data)
                if url:
                    audio_url = url
            except Exception:
                pass
        if not audio_url and bot_id:
            try:
                bot_data = await recall_service.get_bot(str(bot_id))
                records = bot_data.get("recordings") or []
                for r in records:
                    url = _extract_download_url(r)
                    if url:
                        audio_url = url
                        break
            except Exception:
                pass

    if not audio_url:
        return {"status": "ignored"}

    from sqlalchemy import select as sql_select
    result = await db.execute(sql_select(Meeting).where(Meeting.id == meeting_id_int))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    task_id = None
    if audio_url:
        try:
            file_path = await download_audio(audio_url, meeting_id_int)
            meeting.audio_file_path = file_path
            meeting.audio_url = audio_url
            meeting.status = "recording_completed"
            await db.flush()
            await db.commit()
            task = transcribe_audio_task.delay(meeting_id_int)
            task_id = str(task.id)
        except Exception:
            meeting.audio_url = audio_url
            meeting.status = "recording_completed"
            await db.flush()
            await db.commit()
            task = transcribe_audio_from_url_task.delay(meeting_id_int, audio_url)
            task_id = str(task.id)
    else:
        meeting.status = "recording_completed"
        await db.flush()
        await db.commit()
        task = transcribe_audio_task.delay(meeting_id_int)
        task_id = str(task.id)

    return {"status": "accepted", "meeting_id": meeting_id_int, "task_id": task_id}


@router.get("/bot/{bot_id}")
async def get_bot(bot_id: str):
    try:
        data = await recall_service.get_bot(bot_id)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel


class IngestRecordingRequest(BaseModel):
    recording_id: str
    bot_id: str | None = None
    download_url: str | None = None


@router.post("/ingest-recording")
async def ingest_recording(request: IngestRecordingRequest, db: AsyncSession = Depends(get_db)):
    def _extract_download_url(rec: dict) -> str | None:
        url = rec.get("download_url") or rec.get("audio_url") or rec.get("url")
        if url:
            return url
        ms = rec.get("media_shortcuts") or {}
        for key in ("audio_mixed", "video_mixed", "video_mixed_mp4"):
            obj = ms.get(key)
            if isinstance(obj, dict):
                data = obj.get("data") or {}
                dl = data.get("download_url")
                if dl:
                    return dl
        return None

    download_url = request.download_url
    if not download_url:
        try:
            rec_data = await recall_service.get_recording(str(request.recording_id))
            download_url = _extract_download_url(rec_data) or rec_data.get("download_url")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch recording: {str(e)}")

    if not download_url:
        raise HTTPException(status_code=400, detail="No download URL available for recording")

    meeting_id = None
    bot_id = request.bot_id
    if bot_id:
        try:
            import redis
            from app.config import settings
            r = redis.Redis.from_url(settings.redis_url)
            mapped = r.get(f"recall:bot:{bot_id}")
            if mapped:
                meeting_id = int(mapped.decode("utf-8"))
        except Exception:
            pass
        if not meeting_id:
            try:
                bot_data = await recall_service.get_bot(str(bot_id))
                ext = bot_data.get("external_id") or (bot_data.get("metadata") or {}).get("meeting_id")
                if ext:
                    meeting_id = int(str(ext))
            except Exception:
                pass

    if not meeting_id:
        raise HTTPException(status_code=400, detail="Unable to resolve meeting_id from bot_id")

    from sqlalchemy import select as sql_select
    result = await db.execute(sql_select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.audio_url = download_url
    meeting.status = "recording_completed"
    await db.flush()
    await db.commit()

    task = transcribe_audio_from_url_task.delay(meeting_id, download_url)
    return {"status": "accepted", "meeting_id": meeting_id, "task_id": str(task.id)}