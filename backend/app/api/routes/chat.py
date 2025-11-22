import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.meeting_agent import create_meeting_agent

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@router.post("/chat")
async def chat(request: ChatRequest):
    agent = create_meeting_agent()

    # Get the last user message
    user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break

    if not user_message:
        return {"error": "No user message found"}

    async def generate():
        try:
            response = await agent.run(user_message)

            # Stream in Vercel AI SDK format
            # Data format: 0:"text chunk"
            chunks = [response[i:i+50] for i in range(0, len(response), 50)]

            for chunk in chunks:
                # Escape special characters for JSON
                escaped = json.dumps(chunk)
                yield f'0:{escaped}\n'

        except Exception as e:
            error_msg = json.dumps(str(e))
            yield f'0:{error_msg}\n'

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "X-Vercel-AI-Data-Stream": "v1",
        }
    )


@router.post("/chat/non-streaming")
async def chat_non_streaming(request: ChatRequest):
    agent = create_meeting_agent()

    user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.content
            break

    if not user_message:
        return {"error": "No user message found"}

    response = await agent.run(user_message)

    return {
        "id": "msg-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response
                },
                "finish_reason": "stop"
            }
        ]
    }
