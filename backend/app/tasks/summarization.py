from sqlalchemy import select

from app.celery_app import celery_app
from app.models.meeting import Meeting, Transcript, Summary
from app.services.summarization import generate_meeting_summary_sync
from app.tasks.transcription import get_sync_session


@celery_app.task(bind=True)
def generate_summary_task(self, meeting_id: int):
    session = get_sync_session()

    try:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        transcript = session.execute(
            select(Transcript).where(Transcript.meeting_id == meeting_id)
        ).scalar_one_or_none()

        if not transcript:
            raise ValueError(f"No transcript found for meeting {meeting_id}")

        meeting.status = "summarizing"
        session.commit()

        # Generate summary
        result = generate_meeting_summary_sync(transcript.text)

        # Save summary
        summary = Summary(
            meeting_id=meeting_id,
            text=result.get("summary", ""),
            action_items=result.get("action_items", []),
            decisions=result.get("decisions", [])
        )
        session.add(summary)

        meeting.status = "completed"
        session.commit()

        return {"status": "success", "meeting_id": meeting_id}

    except Exception as e:
        meeting = session.execute(
            select(Meeting).where(Meeting.id == meeting_id)
        ).scalar_one_or_none()
        if meeting:
            meeting.status = "summarization_failed"
            session.commit()
        raise

    finally:
        session.close()
