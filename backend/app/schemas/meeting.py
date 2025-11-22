from datetime import datetime
from pydantic import BaseModel


class ParticipantCreate(BaseModel):
    name: str
    email: str


class ParticipantResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class MeetingCreate(BaseModel):
    title: str
    audio_url: str | None = None
    participants: list[ParticipantCreate] = []


class TranscriptResponse(BaseModel):
    id: int
    text: str
    segments: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActionItem(BaseModel):
    task: str
    assignee: str | None = None
    deadline: str | None = None


class SummaryResponse(BaseModel):
    id: int
    text: str
    action_items: list[ActionItem] | None = None
    decisions: list[str] | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class MeetingResponse(BaseModel):
    id: int
    title: str
    date: datetime
    audio_url: str | None = None
    status: str
    created_at: datetime
    transcript: TranscriptResponse | None = None
    summary: SummaryResponse | None = None
    participants: list[ParticipantResponse] = []

    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    id: int
    title: str
    date: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    meeting_id: int
    status: str
    has_transcript: bool
    has_summary: bool


class FollowupRequest(BaseModel):
    subject: str | None = None
    additional_message: str | None = None
