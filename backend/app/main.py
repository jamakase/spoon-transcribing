from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import meetings, chat, zoom, streaming, recall, twins

app = FastAPI(title="Meeting Notes Summarizer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(zoom.router, prefix="/zoom", tags=["zoom"])
app.include_router(streaming.router, prefix="/streaming", tags=["streaming"])
app.include_router(recall.router, prefix="/recall", tags=["recall"])
app.include_router(twins.router, prefix="/api", tags=["twins"])


@app.get("/health")
async def health():
    return {"status": "ok"}
