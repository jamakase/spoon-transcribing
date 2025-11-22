import asyncio
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import engine
from app.models.meeting import Meeting, Transcript
from app.services.transcription import download_audio, transcribe_audio_file


def get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import settings

    sync_url = settings.database_url.replace("+asyncpg", "")
    sync_engine = create_engine(sync_url)
    SessionLocal = sessionmaker(bind=sync_engine)
    return SessionLocal()


@celery_app.task(bind=True)
def transcribe_audio_task(self, meeting_id: int):
    session = get_sync_session()

    try:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting.status = "transcribing"
        session.commit()

        # Get audio file path
        if meeting.audio_url:
            file_path = asyncio.run(download_audio(meeting.audio_url, meeting_id))
        elif meeting.audio_file_path:
            file_path = meeting.audio_file_path
        else:
            raise ValueError("No audio source available")

        # Transcribe
        result = transcribe_audio_file(file_path)

        existing = session.execute(
            select(Transcript).where(Transcript.meeting_id == meeting_id)
        ).scalar_one_or_none()
        if existing:
            existing.text = result["text"]
            existing.segments = result["segments"]
            transcript = existing
        else:
            transcript = Transcript(
                meeting_id=meeting_id,
                text=result["text"],
                segments=result["segments"]
            )
            session.add(transcript)

        meeting.status = "transcribed"
        session.commit()

        return {"status": "success", "meeting_id": meeting_id}

    except Exception as e:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()
        if meeting:
            meeting.status = "transcription_failed"
            session.commit()
        raise

    finally:
        session.close()


@celery_app.task(bind=True)
def transcribe_audio_from_url_task(self, meeting_id: int, source_url: str):
    session = get_sync_session()

    try:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting.status = "transcribing"
        session.commit()

        file_path = asyncio.run(download_audio(source_url, meeting_id))
        meeting.audio_file_path = file_path
        meeting.audio_url = None
        session.commit()

        result = transcribe_audio_file(file_path)

        existing = session.execute(
            select(Transcript).where(Transcript.meeting_id == meeting_id)
        ).scalar_one_or_none()
        if existing:
            existing.text = result["text"]
            existing.segments = result["segments"]
        else:
            transcript = Transcript(
                meeting_id=meeting_id,
                text=result["text"],
                segments=result["segments"]
            )
            session.add(transcript)

        meeting.status = "transcribed"
        session.commit()

        return {"status": "success", "meeting_id": meeting_id}

    except Exception:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()
        if meeting:
            meeting.status = "transcription_failed"
            session.commit()
        raise

    finally:
        session.close()
