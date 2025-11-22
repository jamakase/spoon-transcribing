from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserAccess(Base):
    __tablename__ = "user_access"

    id: Mapped[int] = mapped_column(primary_key=True)
    pubkey: Mapped[str] = mapped_column(String(255))
    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)