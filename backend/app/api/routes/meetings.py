import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.meeting import Meeting, Participant, Summary
from app.schemas.meeting import (
    MeetingCreate,
    MeetingResponse,
    MeetingListResponse,
    StatusResponse,
    FollowupRequest,
)
from app.services.recall import recall_service
import redis
from app.tasks.email import send_followup_task

router = APIRouter()


@router.post("", response_model=MeetingResponse)
async def create_meeting(
    meeting_url: str = Form(...),
    title: str | None = Form(None),
    participant_names: list[str] = Form([]),
    participant_emails: list[str] = Form([]),
    db: AsyncSession = Depends(get_db)
):
    meeting = Meeting(title=title or "Meeting", audio_url=None)

    db.add(meeting)
    await db.flush()

    # Add participants
    for name, email in zip(participant_names, participant_emails):
        participant = Participant(meeting_id=meeting.id, name=name, email=email)
        db.add(participant)

    await db.commit()
    await db.refresh(meeting)

    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.participants),
            selectinload(Meeting.transcript),
            selectinload(Meeting.summary),
        )
        .where(Meeting.id == meeting.id)
    )
    meeting = result.scalar_one()

    try:
        data = await recall_service.start_bot(
            meeting_url=meeting_url,
            bot_name=(title or "Meeting Bot"),
            external_id=str(meeting.id),
        )
        try:
            bot_id = data.get("id")
            if bot_id:
                r = redis.Redis.from_url(settings.redis_url)
                r.set(f"recall:bot:{bot_id}", str(meeting.id))
        except Exception:
            pass
        meeting.status = "recording"
        await db.flush()
        await db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return meeting


@router.get("", response_model=list[MeetingListResponse])
async def list_meetings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).order_by(Meeting.created_at.desc()))
    meetings = result.scalars().all()
    return meetings


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.transcript),
            selectinload(Meeting.summary),
            selectinload(Meeting.participants)
        )
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    await db.delete(meeting)
    await db.commit()

    return {"status": "deleted", "meeting_id": meeting_id}




@router.get("/{meeting_id}/status", response_model=StatusResponse)
async def get_meeting_status(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.transcript), selectinload(Meeting.summary))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return StatusResponse(
        meeting_id=meeting_id,
        status=meeting.status,
        has_transcript=meeting.transcript is not None,
        has_summary=meeting.summary is not None
    )


@router.post("/{meeting_id}/send-followup")
async def send_followup(
    meeting_id: int,
    request: FollowupRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    result = await db.execute(select(Summary).where(Summary.meeting_id == meeting_id))
    summary = result.scalar_one_or_none()

    if not summary:
        raise HTTPException(status_code=400, detail="Meeting must be summarized first")

    task = send_followup_task.delay(
        meeting_id,
        subject=request.subject,
        additional_message=request.additional_message
    )

    return {"status": "email_sending", "meeting_id": meeting_id, "task_id": task.id}
