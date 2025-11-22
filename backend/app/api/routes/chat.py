from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uuid
from sqlalchemy import select

from app.services.meeting_agent import create_meeting_agent
from app.database import async_session
from app.models.chat import Conversation, ChatMessage

router = APIRouter()


class MessagePart(BaseModel):
    type: str
    text: str | None = None

    class Config:
        extra = "allow"


class Message(BaseModel):
    role: str
    content: str | None = None
    parts: list[MessagePart] | None = None

    class Config:
        extra = "allow"

    def get_text(self) -> str:
        if self.content:
            return self.content
        if self.parts:
            return "".join(part.text for part in self.parts if part.type == "text" and part.text)
        return ""


class ChatRequest(BaseModel):
    messages: list[Message]
    conversation_id: str | None = None


@router.post("/chat")
async def chat(request: ChatRequest):
    agent = create_meeting_agent()
    conversation_id = request.conversation_id or str(uuid.uuid4())

    user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.get_text()
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    async with async_session() as session:
        existing = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = existing.scalar_one_or_none()
        if not conv:
            conv = Conversation(id=conversation_id)
            session.add(conv)
        session.add(ChatMessage(conversation_id=conversation_id, role="user", content=user_message))
        await session.commit()

    async def generate():
        try:
            response = await agent.run(user_message)

            # Stream plain text chunks for AI SDK v5 TextStreamChatTransport
            chunks = [response[i:i+50] for i in range(0, len(response), 50)]

            for chunk in chunks:
                yield chunk

            try:
                async with async_session() as session:
                    session.add(ChatMessage(conversation_id=conversation_id, role="assistant", content=response))
                    await session.commit()
            except Exception:
                pass

        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
    )


@router.post("/chat/non-streaming")
async def chat_non_streaming(request: ChatRequest):
    agent = create_meeting_agent()
    conversation_id = request.conversation_id or str(uuid.uuid4())

    user_message = ""
    for msg in reversed(request.messages):
        if msg.role == "user":
            user_message = msg.get_text()
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    async with async_session() as session:
        existing = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = existing.scalar_one_or_none()
        if not conv:
            conv = Conversation(id=conversation_id)
            session.add(conv)
        session.add(ChatMessage(conversation_id=conversation_id, role="user", content=user_message))
        await session.commit()

    response = await agent.run(user_message)

    async with async_session() as session:
        session.add(ChatMessage(conversation_id=conversation_id, role="assistant", content=response))
        await session.commit()

    return {
        "id": "msg-1",
        "object": "chat.completion",
        "conversation_id": conversation_id,
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


@router.get("/chat/history/{conversation_id}")
async def chat_history(conversation_id: str):
    try:
        async with async_session() as session:
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.conversation_id == conversation_id)
                .order_by(ChatMessage.created_at.asc())
            )
            rows = result.scalars().all()
            messages = [{"role": r.role, "content": r.content, "created_at": r.created_at.isoformat()} for r in rows]
            return {"conversation_id": conversation_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
