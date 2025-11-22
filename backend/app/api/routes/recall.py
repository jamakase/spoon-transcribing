from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json

from app.database import get_db
from app.models.meeting import Meeting
from app.tasks.transcription import transcribe_audio_task
from app.services.recall import recall_service


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
        return {"status": "ignored"}

    from sqlalchemy import select as sql_select
    result = await db.execute(sql_select(Meeting).where(Meeting.id == meeting_id_int))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    meeting.audio_url = audio_url
    meeting.status = "recording_completed"
    await db.flush()
    await db.commit()

    task = transcribe_audio_task.delay(meeting_id_int)
    return {"status": "accepted", "meeting_id": meeting_id_int, "task_id": str(task.id)}