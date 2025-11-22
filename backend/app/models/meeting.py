from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")

    # Streaming bot fields
    zoom_meeting_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    zoom_meeting_uuid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_streaming: Mapped[bool] = mapped_column(default=False)
    bot_joined_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    bot_left_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transcript: Mapped["Transcript | None"] = relationship(back_populates="meeting", uselist=False)
    summary: Mapped["Summary | None"] = relationship(back_populates="meeting", uselist=False)
    participants: Mapped[list["Participant"]] = relationship(back_populates="meeting")


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    text: Mapped[str] = mapped_column(Text)
    segments: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    meeting: Mapped["Meeting"] = relationship(back_populates="transcript")


class Summary(Base):
    __tablename__ = "summaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    text: Mapped[str] = mapped_column(Text)
    action_items: Mapped[list | None] = mapped_column(JSON, nullable=True)
    decisions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    meeting: Mapped["Meeting"] = relationship(back_populates="summary")


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))

    meeting: Mapped["Meeting"] = relationship(back_populates="participants")
