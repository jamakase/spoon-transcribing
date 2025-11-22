from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import hmac
import hashlib
import base64
import aiohttp
import logging
import json

from app.database import get_db
from app.models.meeting import Meeting
from app.config import settings
from app.tasks.transcription import transcribe_audio_task
from app.tasks.zoom_bot import start_zoom_bot_task

logger = logging.getLogger(__name__)

router = APIRouter()


def _verify_zoom_signature(signature: str | None, ts: str | None, body: bytes) -> bool:
    if settings.zoom_skip_signature_verification:
        logger.warning("⚠️  ZOOM_SKIP_SIGNATURE_VERIFICATION is True - skipping signature check (dev/test only!)")
        return True

    if not settings.zoom_webhook_secret_token:
        logger.warning("⚠️  No ZOOM_WEBHOOK_SECRET_TOKEN configured - skipping signature verification")
        return True
    if not signature or not ts:
        logger.error("❌ Missing signature or timestamp in webhook headers")
        logger.error(f"   Signature: {signature}")
        logger.error(f"   Timestamp: {ts}")
        return False

    message = b"v0:" + ts.encode() + b":" + body
    digest = hmac.new(settings.zoom_webhook_secret_token.encode(), message, hashlib.sha256).digest()
    expected = "v0=" + base64.b64encode(digest).decode()

    logger.info(f"🔐 Signature Verification")
    logger.info(f"   Received:  {signature}")
    logger.info(f"   Expected:  {expected}")
    logger.info(f"   Secret Token: {settings.zoom_webhook_secret_token[:10]}...{settings.zoom_webhook_secret_token[-4:]}")

    is_valid = hmac.compare_digest(signature, expected)
    if is_valid:
        logger.info("✅ Signature verified")
    else:
        logger.error("❌ Signature mismatch!")
        logger.error(f"   Timestamp: {ts}")
        logger.error(f"   Body length: {len(body)} bytes")

    return is_valid


@router.post("/webhook")
async def zoom_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    raw_body = await request.body()
    signature = request.headers.get("x-zm-signature")
    timestamp = request.headers.get("x-zm-request-timestamp")

    logger.info("=" * 80)
    logger.info("📨 ZOOM WEBHOOK RECEIVED")
    logger.info("=" * 80)
    logger.info(f"Signature: {signature}")
    logger.info(f"Timestamp: {timestamp}")

    if not _verify_zoom_signature(signature, timestamp, raw_body):
        logger.error("❌ Invalid signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    logger.info("✅ Signature verified")

    payload = await request.json()
    logger.info(f"📦 Full Payload: {json.dumps(payload, indent=2)}")

    event = payload.get("event")
    logger.info(f"📌 Event type: {event}")

    # Handle meeting started event
    if event == "meeting.started":
        logger.info("🎤 Meeting started event detected")
        obj = (payload.get("payload") or {}).get("object") or {}
        meeting_id = obj.get("id")
        meeting_uuid = obj.get("uuid")
        topic = obj.get("topic") or "Zoom Meeting"

        logger.info(f"Meeting ID: {meeting_id}")
        logger.info(f"Meeting UUID: {meeting_uuid}")
        logger.info(f"Topic: {topic}")

        if not meeting_id or not meeting_uuid:
            logger.error("Missing meeting ID or UUID")
            return {"status": "ignored", "reason": "Missing meeting ID or UUID"}

        # Create meeting record
        meeting = Meeting(
            title=topic,
            zoom_meeting_id=str(meeting_id),
            zoom_meeting_uuid=str(meeting_uuid),
        )
        db.add(meeting)
        await db.flush()
        await db.commit()
        await db.refresh(meeting)

        logger.info(f"✅ Meeting created in DB with ID: {meeting.id}")

        # Queue bot task
        logger.info(f"🤖 Queuing bot start task for meeting {meeting.id}")
        task = start_zoom_bot_task.delay(meeting.id, str(meeting_id), str(meeting_uuid))
        logger.info(f"✅ Bot task queued with ID: {task.id}")

        return {"status": "accepted", "meeting_id": meeting.id, "task_id": str(task.id)}

    # Handle recording completed event (legacy)
    elif event and "recording.completed" in event:
        logger.info("🎬 Recording completed event detected")
        obj = (payload.get("payload") or {}).get("object") or {}
        files = obj.get("recording_files") or []
        title = obj.get("topic") or "Zoom Meeting"

        logger.info(f"Recording files count: {len(files)}")

        chosen = None
        for f in files:
            t = f.get("recording_type")
            ft = f.get("file_type")
            logger.info(f"  - Recording type: {t}, File type: {ft}")
            if t == "audio_only" or ft == "M4A":
                chosen = f
                break

        if not chosen:
            logger.error("❌ No audio recording found in payload")
            raise HTTPException(status_code=400, detail="No audio recording in payload")

        download_url = chosen.get("download_url")
        if not download_url:
            logger.error("❌ No download_url in payload")
            raise HTTPException(status_code=400, detail="No download_url in payload")

        logger.info(f"✅ Found audio recording: {download_url}")

        meeting = Meeting(title=title, audio_url=download_url)
        db.add(meeting)
        await db.flush()
        await db.commit()
        await db.refresh(meeting)

        logger.info(f"✅ Meeting created with ID: {meeting.id}")

        logger.info(f"🤖 Queuing transcription task")
        task = transcribe_audio_task.delay(meeting.id)
        logger.info(f"✅ Transcription task queued with ID: {task.id}")

        return {"status": "accepted", "meeting_id": meeting.id, "task_id": str(task.id)}

    else:
        logger.info(f"⏭️  Event not handled: {event}")
        return {"status": "ignored", "reason": f"Event {event} not handled"}


@router.get("/oauth/authorize")
async def zoom_oauth_authorize():
    if not settings.zoom_client_id or not settings.zoom_redirect_uri:
        raise HTTPException(status_code=500, detail="Zoom OAuth not configured")
    url = (
        "https://zoom.us/oauth/authorize"
        f"?response_type=code&client_id={settings.zoom_client_id}"
        f"&redirect_uri={settings.zoom_redirect_uri}"
    )
    return RedirectResponse(url)


@router.get("/oauth/callback")
async def zoom_oauth_callback(code: str | None = None):
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    if not settings.zoom_client_id or not settings.zoom_client_secret or not settings.zoom_redirect_uri:
        raise HTTPException(status_code=500, detail="Zoom OAuth not configured")

    token_url = "https://zoom.us/oauth/token"
    auth = base64.b64encode(f"{settings.zoom_client_id}:{settings.zoom_client_secret}".encode()).decode()
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.zoom_redirect_uri,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, data=data, headers={"Authorization": f"Basic {auth}"}) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise HTTPException(status_code=resp.status, detail=text)
            payload = await resp.json()

    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="No access token returned")

    settings.zoom_access_token = access_token
    if refresh_token:
        settings.zoom_refresh_token = refresh_token

    return {"status": "ok", "access_token_set": True}