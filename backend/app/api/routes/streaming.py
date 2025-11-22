"""Routes for managing streaming transcription and Zoom bot."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.models.meeting import Meeting
from app.tasks.zoom_bot import start_zoom_bot_task, stop_zoom_bot_task

router = APIRouter()


class StartBotRequest(BaseModel):
    """Request to start bot in a Zoom meeting."""

    title: str
    zoom_meeting_id: str
    zoom_meeting_uuid: str


class BotResponse(BaseModel):
    """Response for bot operations."""

    status: str
    message: str
    meeting_id: int


@router.post("/bot/start", response_model=BotResponse)
async def start_bot(request: StartBotRequest, db: AsyncSession = Depends(get_db)):
    """Start the bot in a Zoom meeting and begin real-time transcription.

    This creates a new meeting record and triggers the bot to join the Zoom meeting.
    The bot will start streaming audio for real-time transcription.

    Args:
        request: Start bot request with meeting details
        db: Database session

    Returns:
        Response with meeting ID and status
    """
    try:
        # Create meeting record
        meeting = Meeting(
            title=request.title,
            zoom_meeting_id=request.zoom_meeting_id,
            zoom_meeting_uuid=request.zoom_meeting_uuid,
        )
        db.add(meeting)
        await db.flush()
        await db.commit()
        await db.refresh(meeting)

        # Queue bot task
        start_zoom_bot_task.delay(meeting.id, request.zoom_meeting_id, request.zoom_meeting_uuid)

        return {
            "status": "success",
            "message": f"Bot starting for meeting: {request.title}",
            "meeting_id": meeting.id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")


@router.post("/bot/stop/{meeting_id}", response_model=BotResponse)
async def stop_bot(meeting_id: int, db: AsyncSession = Depends(get_db)):
    """Stop the bot in a Zoom meeting and finalize the transcript.

    Args:
        meeting_id: Database meeting ID
        db: Database session

    Returns:
        Response with status
    """
    try:
        meeting = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = meeting.scalar_one_or_none()

        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting {meeting_id} not found")

        if not meeting.is_streaming:
            raise HTTPException(status_code=400, detail="Meeting is not currently streaming")

        # Queue stop task
        stop_zoom_bot_task.delay(meeting_id)

        return {
            "status": "success",
            "message": f"Bot stopping for meeting: {meeting.title}",
            "meeting_id": meeting_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")


@router.get("/meetings/{meeting_id}/status")
async def get_meeting_status(meeting_id: int, db: AsyncSession = Depends(get_db)):
    """Get current status of a meeting.

    Args:
        meeting_id: Database meeting ID
        db: Database session

    Returns:
        Meeting status information
    """
    try:
        meeting = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = meeting.scalar_one_or_none()

        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting {meeting_id} not found")

        return {
            "meeting_id": meeting.id,
            "title": meeting.title,
            "status": meeting.status,
            "is_streaming": meeting.is_streaming,
            "zoom_meeting_id": meeting.zoom_meeting_id,
            "bot_joined_at": meeting.bot_joined_at,
            "bot_left_at": meeting.bot_left_at,
            "created_at": meeting.created_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get meeting status: {str(e)}")
