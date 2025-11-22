# Webhook & Bot Debugging Guide

## What's Been Added

We've added comprehensive logging to help debug the bot joining process. Here's what will appear in your logs when a webhook is received.

## Expected Log Output When Webhook is Received

### 1. Webhook Handler Logs (FastAPI/Uvicorn)

When a `meeting.started` event is received:

```
================================================================================
📨 ZOOM WEBHOOK RECEIVED
================================================================================
Signature: <signature>
Timestamp: <timestamp>
✅ Signature verified
📦 Full Payload: {...full json payload...}
📌 Event type: meeting.started
🎤 Meeting started event detected
Meeting ID: 12345678
Meeting UUID: abc-def-ghi
Topic: Your Meeting Title
✅ Meeting created in DB with ID: 5
🤖 Queuing bot start task for meeting 5
✅ Bot task queued with ID: abc-123-def-456
```

### 2. Celery Worker Task Logs

When the `start_zoom_bot_task` is executed by the worker:

```
================================================================================
🤖 START_ZOOM_BOT_TASK - Received
================================================================================
Meeting ID: 5
Zoom Meeting ID: 12345678
Zoom Meeting UUID: abc-def-ghi
📋 Fetching meeting from database...
✅ Found meeting: Your Meeting Title
📝 Updating meeting with streaming status...
✅ Meeting status updated to 'streaming'
🚀 TODO: Call Zoom API to start bot in meeting
================================================================================
✅ TASK COMPLETED SUCCESSFULLY
================================================================================
🔒 Session closed
```

## How to Monitor the Logs

### Option 1: Watch the Dev Console
The logs appear in your terminal where you run `make dev`. Watch both the FastAPI output (top) and Celery worker output (bottom).

### Option 2: Check Your ngrok Logs
When sending test webhooks through ngrok, you'll see:
```
ngrok: connected to http://127.0.0.1:8001
events:
- webhook received from Zoom
- 200 OK response
```

## Debugging Checklist

If the bot is not joining:

### ✅ Check 1: Webhook is Received
Look for: `📨 ZOOM WEBHOOK RECEIVED`
- If missing: Verify ngrok URL is correct in Zoom webhook configuration
- If present: Move to Check 2

### ✅ Check 2: Event Type is Correct
Look for: `📌 Event type: meeting.started`
- If shows different event: Check Zoom webhook configuration to send `meeting.started` event
- If correct: Move to Check 3

### ✅ Check 3: Meeting Created in DB
Look for: `✅ Meeting created in DB with ID: X`
- If missing: Check database connection and migrations
- If present: Move to Check 4

### ✅ Check 4: Task Queued
Look for: `✅ Bot task queued with ID:`
- If missing: Check Celery/Redis connection
- If present: Move to Check 5

### ✅ Check 5: Celery Task Executed
Look for: `🤖 START_ZOOM_BOT_TASK - Received`
- If missing: Celery worker not picking up tasks
  - Check if Celery worker is running: `make worker`
  - Check Redis connection
- If present: Move to Check 6

### ✅ Check 6: Bot API Call (Next Step)
Look for: `🚀 TODO: Call Zoom API to start bot in meeting`
- This is where you'll implement the actual Zoom API call to join the meeting
- Once implemented, watch for Zoom API response logs

## Next Steps

The logging is now in place. The next thing to implement is:

1. **Uncomment & Complete the Zoom API Call** in `app/tasks/zoom_bot.py:68-72`
   - Implement `zoom_bot_service.start_meeting_bot()`
   - Add error handling for Zoom API failures

2. **Add Logging to Zoom Bot Service** in `app/services/zoom_bot.py`
   - Log authentication tokens
   - Log API requests/responses
   - Handle rate limiting

3. **Monitor Bot Audio Stream**
   - Once bot joins, you'll need to receive audio stream from Zoom
   - Add logging for audio chunks received
   - Implement streaming transcription

## Log Levels

- 📨 = Info (event received)
- ✅ = Info (success)
- 📌 = Info (status checkpoint)
- 🤖 = Info (bot-related action)
- ❌ = Error (something failed)

## Redis/Celery Debugging

If tasks aren't being picked up:

```bash
# Check Celery worker is running
make worker

# Check Redis connection
redis-cli ping
# Should return: PONG

# Check Celery tasks in queue
redis-cli keys '*'
```

## Common Issues & Solutions

### Issue: "🤖 START_ZOOM_BOT_TASK - Received" never appears
**Solution:**
- Celery worker not running: `make worker`
- Check Redis is running: `docker-compose ps`
- Check task is registered: Look for `app.tasks.zoom_bot.start_zoom_bot_task` in Celery startup logs

### Issue: "Meeting created in DB with ID" but no task log
**Solution:**
- Task may be queued but not executed
- Check Celery worker logs for task pickup
- Ensure `app.tasks.zoom_bot` is in celery_app.include list

### Issue: Signature verification failed
**Solution:**
- Verify `ZOOM_SECRET_TOKEN` matches webhook token in Zoom settings
- Check raw request body hasn't been modified

---

Now when you test with a Zoom webhook, you'll get detailed debugging information to track exactly where the bot joining is failing!
