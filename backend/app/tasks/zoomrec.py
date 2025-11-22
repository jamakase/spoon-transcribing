from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
import logging
import os
import subprocess
import time
from zoneinfo import ZoneInfo

from app.celery_app import celery_app
from app.models.meeting import Meeting
from app.tasks.transcription import transcribe_audio_task


logger = logging.getLogger(__name__)


def get_sync_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.config import settings

    sync_url = settings.database_url.replace("+asyncpg", "")
    sync_engine = create_engine(sync_url)
    SessionLocal = sessionmaker(bind=sync_engine)
    return SessionLocal()


def _write_zoomrec_csv(csv_path: str, zoom_url: str, description: str, duration_minutes: int, tz: str):
    tzinfo = ZoneInfo(tz)
    when = datetime.now(tzinfo) + timedelta(minutes=1)
    weekday = when.strftime("%A").lower()
    time_str = when.strftime("%H:%M")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("weekday;time;duration;id;password;description;record\n")
        f.write(f"{weekday};{time_str};{duration_minutes};{zoom_url};;{description};true\n")


def _find_recording_file(recordings_dir: str) -> str | None:
    if not os.path.isdir(recordings_dir):
        return None
    candidates = []
    for root, _, files in os.walk(recordings_dir):
        for name in files:
            if name.lower().endswith((".mkv", ".mp4", ".webm")):
                candidates.append(os.path.join(root, name))
    if not candidates:
        return None
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]


@celery_app.task(bind=True)
def start_zoomrec_task(self, meeting_id: int, zoom_url: str, duration_minutes: int = 60):
    from app.config import settings

    session = get_sync_session()

    try:
        meeting = session.execute(select(Meeting).where(Meeting.id == meeting_id)).scalar_one_or_none()
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        recordings_dir = os.path.abspath(os.path.join(settings.upload_dir, "zoomrec", f"meeting_{meeting_id}"))
        csv_path = os.path.abspath(os.path.join(recordings_dir, "meetings.csv"))
        description = meeting.title or f"meeting_{meeting_id}"

        _write_zoomrec_csv(csv_path, zoom_url, description, duration_minutes, settings.zoomrec_timezone)

        meeting.status = "recording"
        session.commit()

        cmd = [
            "docker",
            "run",
            "-d",
            "--rm",
            f"--name=zoomrec_meeting_{meeting_id}",
            "--security-opt",
            "seccomp:unconfined",
            "--platform",
            "linux/amd64",
            "-e",
            f"TZ={settings.zoomrec_timezone}",
            "-e",
            f"DISPLAY_NAME={settings.zoom_display_name}",
            "-e",
            "DEBUG=True",
            "-v",
            f"{recordings_dir}:/home/zoomrec/recordings",
            "-v",
            f"{csv_path}:/home/zoomrec/meetings.csv:ro",
            "-p",
            "5901:5901",
            settings.zoomrec_image,
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            container_id = result.stdout.strip()
            logger.info(f"zoomrec container started: {container_id}")
        except Exception as e:
            meeting.status = "recording_failed"
            session.commit()
            raise

        deadline = time.time() + (duration_minutes + 10) * 60
        last_seen = None
        while time.time() < deadline:
            path = _find_recording_file(recordings_dir)
            if path and os.path.isfile(path):
                if last_seen != path:
                    last_seen = path
                if os.path.getsize(path) > 1024 * 1024:
                    break
            time.sleep(15)

        final_file = _find_recording_file(recordings_dir)
        if not final_file:
            meeting.status = "recording_failed"
            session.commit()
            raise RuntimeError("No recording file produced by zoomrec")

        meeting.audio_file_path = final_file
        meeting.status = "recording_completed"
        session.commit()

        task = transcribe_audio_task.delay(meeting_id)

        return {"status": "accepted", "meeting_id": meeting_id, "recording": final_file, "task_id": str(task.id)}

    finally:
        session.close()