from celery import Celery

from app.config import settings

celery_app = Celery(
    "meeting_summarizer",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.transcription", "app.tasks.summarization", "app.tasks.email"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
