from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json
import redis

from app.database import get_db
from app.models.meeting import Meeting
from app.tasks.transcription import transcribe_audio_task, transcribe_audio_from_url_task
from app.services.recall import recall_service
from app.services.transcription import download_audio


router = APIRouter()


class StartRecallRequest(BaseModel):
    url: str
    title: str | None = None


@router.post("/start")
async def start_recall(request: StartRecallRequest, db: AsyncSession = Depends(get_db)):
    try:
        meeting = Meeting(title=request.title or "Meeting")
        db.add(meeting)
        await db.flush()
        await db.commit()
        await db.refresh(meeting)

        data = await recall_service.start_bot(
            meeting_url=request.url,
            bot_name=request.title or "Meeting Bot",
            external_id=str(meeting.id),
        )
        try:
            bot_id = data.get("id")
            if bot_id:
                r = redis.Redis.from_url(settings.redis_url)
                r.set(f"recall:bot:{bot_id}", str(meeting.id))
        except Exception:
            pass
        return {"status": "accepted", "meeting_id": meeting.id, "bot": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            meeting.status = "recording_completed"
            await db.flush()
            await db.commit()
            task = transcribe_audio_task.delay(meeting_id_int)
            task_id = str(task.id)
        except Exception:
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