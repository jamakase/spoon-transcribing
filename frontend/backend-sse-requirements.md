# Backend SSE Requirements for Frontend Integration

The frontend is ready to consume a standard SSE stream. Based on the API docs provided (`docs.md`), the current `streaming` endpoints (`/streaming/bot/start`, `/streaming/bot/stop`) are transactional POST requests.

**I need a specific GET endpoint to subscribe to the real-time events.**

## 1. Endpoint Requirement
Please provide a GET endpoint for SSE subscriptions, for example:
`GET /streaming/meetings/{meeting_id}/events`

## 2. Header Requirements
*   `Content-Type`: `text/event-stream`
*   `Cache-Control`: `no-cache`
*   `Connection`: `keep-alive`
*   `Access-Control-Allow-Origin`: `*` (or your frontend domain)

## 3. Payload Format (The "Contract")
Send events in standard SSE format. The `data` field should be a stringified JSON object with a `type` discriminator.

### Example Stream:

```text
data: {"type": "status", "data": {"status": "connecting"}}
\n\n
data: {"type": "transcript", "data": {"speaker": "Alex", "text": "Hello team", "timestamp": "00:00:01"}}
\n\n
data: {"type": "transcript", "data": {"speaker": "Sarah", "text": "Hi Alex", "timestamp": "00:00:02"}}
\n\n
data: {"type": "summary_update", "data": {"text": "Team greetings exchange..."}}
\n\n
```

## 4. Frontend Hook Ready
I have implemented a React hook `useMeetingStream` that expects this format. 
*   It connects to the URL you provide.
*   It parses `event.data` as JSON.
*   It adds the parsed object to a `messages` array state.

