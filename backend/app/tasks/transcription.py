import asyncio
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import engine
from app.models.meeting import Meeting, Transcript
from app.services.transcription import download_audio, transcribe_audio_file


def _extract_download_url(rec: dict) -> str | None:
    url = rec.get("download_url") or rec.get("audio_url") or rec.get("url")
    if url:
        return url
    ms = rec.get("media_shortcuts") or {}
    for key in ("audio_mixed", "video_mixed_mp4", "video_mixed"):
        obj = ms.get(key)
        if isinstance(obj, dict):
            data = obj.get("data") or {}
            dl = data.get("download_url")
            if dl:
                return dl
    return None


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

        try:
            celery_app.send_task("app.tasks.summarization.generate_summary_task", args=[meeting_id])
        except Exception:
            pass

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
def transcribe_audio_from_url_task(self, meeting_id: int, source_url: str, recording_id: str | None = None):
    session = get_sync_session()

    try:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        meeting.status = "transcribing"
        session.commit()

        # Always try to get a fresh URL from Recall API first since pre-signed URLs expire
        from app.services.recall import recall_service

        download_url = source_url
        if recording_id:
            try:
                # Get fresh URL from recording endpoint
                rec_data = asyncio.run(recall_service.get_recording(str(recording_id)))
                fresh_url = _extract_download_url(rec_data) or rec_data.get("download_url")
                if fresh_url:
                    download_url = fresh_url
            except Exception:
                pass  # Fall back to source_url

        try:
            file_path = asyncio.run(download_audio(download_url, meeting_id))
            meeting.audio_url = download_url
        except Exception as e:
            # If download fails, the URL may be expired
            raise ValueError(f"Failed to download audio: {e}")
        meeting.audio_file_path = file_path
        if not meeting.audio_url:
            meeting.audio_url = source_url
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

        try:
            celery_app.send_task("app.tasks.summarization.generate_summary_task", args=[meeting_id])
        except Exception:
            pass

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
