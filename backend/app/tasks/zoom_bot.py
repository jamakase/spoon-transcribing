"""Celery tasks for Zoom bot management."""

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging

from app.celery_app import celery_app
from app.models.meeting import Meeting
from app.services.zoom_bot import zoom_bot_service

logger = logging.getLogger(__name__)


def get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import settings

    sync_url = settings.database_url.replace("+asyncpg", "")
    sync_engine = create_engine(sync_url)
    SessionLocal = sessionmaker(bind=sync_engine)
    return SessionLocal()


@celery_app.task(bind=True)
def start_zoom_bot_task(self, meeting_id: int, zoom_meeting_id: str, zoom_meeting_uuid: str):
    """Start a bot in a Zoom meeting for real-time transcription.

    Args:
        meeting_id: Database meeting ID
        zoom_meeting_id: Zoom meeting ID (numeric)
        zoom_meeting_uuid: Zoom meeting UUID
    """
    logger.info("=" * 80)
    logger.info(f"🤖 START_ZOOM_BOT_TASK - Received")
    logger.info("=" * 80)
    logger.info(f"Meeting ID: {meeting_id}")
    logger.info(f"Zoom Meeting ID: {zoom_meeting_id}")
    logger.info(f"Zoom Meeting UUID: {zoom_meeting_uuid}")

    session = get_sync_session()

    try:
        logger.info("📋 Fetching meeting from database...")
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            logger.error(f"❌ Meeting {meeting_id} not found in database")
            raise ValueError(f"Meeting {meeting_id} not found")

        logger.info(f"✅ Found meeting: {meeting.title}")

        # Update meeting with Zoom info
        logger.info("📝 Updating meeting with streaming status...")
        from datetime import timezone
        meeting.zoom_meeting_id = zoom_meeting_id
        meeting.zoom_meeting_uuid = zoom_meeting_uuid
        meeting.is_streaming = True
        meeting.bot_joined_at = datetime.now(timezone.utc)
        meeting.status = "streaming"
        session.commit()
        logger.info("✅ Meeting status updated to 'streaming'")

        # Call Zoom API to start bot
        logger.info("🚀 Calling Zoom API to start bot in meeting...")
        try:
            import asyncio
            from app.config import settings

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    zoom_bot_service.start_meeting_bot(
                        meeting_id=zoom_meeting_id,
                        meeting_uuid=zoom_meeting_uuid,
                        bot_jid=settings.zoom_bot_jid,
                    )
                )
                logger.info(f"✅ Bot API call succeeded: {result}")
                from datetime import timezone
                meeting.bot_joined_at = datetime.now(timezone.utc)
                session.commit()
                logger.info(f"✅ Bot join timestamp recorded in database")
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"❌ Failed to start bot via Zoom API: {str(e)}", exc_info=True)
            raise

        logger.info("=" * 80)
        logger.info("✅ TASK COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)

        return {
            "status": "success",
            "meeting_id": meeting_id,
            "zoom_meeting_id": zoom_meeting_id,
        }

    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR IN start_zoom_bot_task")
        logger.error("=" * 80)
        logger.error(f"Error: {str(e)}", exc_info=True)

        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()
        if meeting:
            meeting.status = "bot_failed"
            session.commit()
            logger.error(f"Meeting {meeting_id} marked as failed")
        raise

    finally:
        session.close()
        logger.info("🔒 Session closed")


@celery_app.task(bind=True)
def stop_zoom_bot_task(self, meeting_id: int):
    """Stop the bot in a Zoom meeting.

    Args:
        meeting_id: Database meeting ID
    """
    from datetime import timezone
    session = get_sync_session()

    try:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting.is_streaming = False
        meeting.bot_left_at = datetime.now(timezone.utc)
        meeting.status = "streaming_ended"
        session.commit()

        # TODO: Call Zoom API to stop bot if needed

        return {"status": "success", "meeting_id": meeting_id}

    except Exception as e:
        raise

    finally:
        session.close()


@celery_app.task(bind=True)
def save_transcript_segment_task(
    self, meeting_id: int, text: str, timestamp: str, confidence: float = 0.0
):
    """Save a transcription segment to the database.

    Args:
        meeting_id: Database meeting ID
        text: Transcribed text segment
        timestamp: ISO format timestamp
        confidence: Confidence score from transcription model
    """
    session = get_sync_session()

    try:
        from app.models.meeting import Transcript

        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # Get or create transcript
        transcript = session.execute(
            select(Transcript).where(Transcript.meeting_id == meeting_id)
        ).scalar_one_or_none()

        if not transcript:
            transcript = Transcript(
                meeting_id=meeting_id,
                text=text,
                segments=[
                    {
                        "text": text,
                        "timestamp": timestamp,
                        "confidence": confidence,
                    }
                ],
            )
            session.add(transcript)
        else:
            # Append to existing transcript
            transcript.text += " " + text
            if not transcript.segments:
                transcript.segments = []
            transcript.segments.append(
                {
                    "text": text,
                    "timestamp": timestamp,
                    "confidence": confidence,
                }
            )

        session.commit()
        return {"status": "success", "meeting_id": meeting_id}

    except Exception as e:
        raise

    finally:
        session.close()
