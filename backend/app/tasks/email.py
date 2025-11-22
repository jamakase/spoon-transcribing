from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.celery_app import celery_app
from app.models.meeting import Meeting, Summary, Participant
from app.services.email import send_followup_email
from app.tasks.transcription import get_sync_session


@celery_app.task(bind=True)
def send_followup_task(self, meeting_id: int, subject: str | None = None, additional_message: str | None = None):
    session = get_sync_session()

    try:
        meeting = session.execute(
            select(Meeting)
            .options(joinedload(Meeting.participants))
            .where(Meeting.id == meeting_id)
        ).unique().scalar_one_or_none()

        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        summary = session.execute(
            select(Summary).where(Summary.meeting_id == meeting_id)
        ).scalar_one_or_none()

        if not summary:
            raise ValueError(f"No summary found for meeting {meeting_id}")

        if not meeting.participants:
            raise ValueError(f"No participants found for meeting {meeting_id}")

        to_emails = [p.email for p in meeting.participants]
        email_subject = subject or f"Meeting Summary: {meeting.title}"

        result = send_followup_email(
            to_emails=to_emails,
            subject=email_subject,
            meeting_title=meeting.title,
            summary_text=summary.text,
            action_items=summary.action_items or [],
            decisions=summary.decisions or [],
            additional_message=additional_message
        )

        return {"status": "success", "meeting_id": meeting_id, "email_result": result}

    finally:
        session.close()
