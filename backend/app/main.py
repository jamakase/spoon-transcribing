from fastapi import FastAPI
from app.api.routes import meetings

app = FastAPI(title="Meeting Notes Summarizer", version="1.0.0")

app.include_router(meetings.router, prefix="/meetings", tags=["meetings"])


@app.get("/health")
async def health():
    return {"status": "ok"}
