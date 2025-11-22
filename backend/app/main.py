from fastapi import FastAPI
from app.api.routes import meetings, chat

app = FastAPI(title="Meeting Notes Summarizer", version="1.0.0")

app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/health")
async def health():
    return {"status": "ok"}
