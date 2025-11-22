from fastapi import FastAPI
from app.api.routes import meetings, chat, zoom, streaming, recall

app = FastAPI(title="Meeting Notes Summarizer", version="1.0.0")

app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(zoom.router, prefix="/zoom", tags=["zoom"])
app.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
app.include_router(recall.router, prefix="/recall", tags=["recall"])


@app.get("/health")
async def health():
    return {"status": "ok"}
