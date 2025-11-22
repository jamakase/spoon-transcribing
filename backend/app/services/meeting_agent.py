from spoon_ai.agents import SpoonReactAI
from spoon_ai.chat import ChatBot
from spoon_ai.tools import BaseTool
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.meeting import Meeting, Transcript, Summary, Participant
from app.tasks.transcription import get_sync_session
from app.tasks.email import send_followup_task
from app.services.recall import recall_service
import redis


class ListMeetingsTool(BaseTool):
    name: str = "list_meetings"
    description: str = "List all meetings with their status. Returns meeting id, title, date, and status."
    parameters: dict = Field(default={"type": "object", "properties": {}}, description="No parameters required")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            result = session.execute(
                select(Meeting).order_by(Meeting.created_at.desc()).limit(20)
            )
            meetings = result.scalars().all()

            if not meetings:
                return "No meetings found."

            output = "Meetings:\n"
            for m in meetings:
                output += f"- ID: {m.id}, Title: {m.title}, Date: {m.date}, Status: {m.status}\n"
            return output
        finally:
            session.close()


class GetMeetingDetailsTool(BaseTool):
    name: str = "get_meeting_details"
    description: str = "Get detailed information about a specific meeting including transcript and summary. Requires meeting_id."
    meeting_id: int = Field(description="The ID of the meeting to retrieve")
    parameters: dict = Field(default={"type": "object", "properties": {"meeting_id": {"type": "integer", "description": "The ID of the meeting to retrieve"}}, "required": ["meeting_id"]}, description="Tool parameters")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            result = session.execute(
                select(Meeting)
                .options(
                    selectinload(Meeting.transcript),
                    selectinload(Meeting.summary),
                    selectinload(Meeting.participants)
                )
                .where(Meeting.id == self.meeting_id)
            )
            meeting = result.scalar_one_or_none()

            if not meeting:
                return f"Meeting {self.meeting_id} not found."

            output = f"Meeting: {meeting.title}\n"
            output += f"Date: {meeting.date}\n"
            output += f"Status: {meeting.status}\n"

            if meeting.participants:
                output += f"Participants: {', '.join([p.name for p in meeting.participants])}\n"

            if meeting.transcript:
                output += f"\nTranscript:\n{meeting.transcript.text[:2000]}{'...' if len(meeting.transcript.text) > 2000 else ''}\n"

            if meeting.summary:
                output += f"\nSummary:\n{meeting.summary.text}\n"
                if meeting.summary.action_items:
                    output += "\nAction Items:\n"
                    for item in meeting.summary.action_items:
                        output += f"- {item.get('task', '')} ({item.get('assignee', 'unassigned')})\n"
                if meeting.summary.decisions:
                    output += "\nDecisions:\n"
                    for decision in meeting.summary.decisions:
                        output += f"- {decision}\n"

            return output
        finally:
            session.close()


class GetLastDiscussionTool(BaseTool):
    name: str = "get_last_discussion"
    description: str = "Get what was discussed last time. Returns latest meeting summary or transcript snippet."
    parameters: dict = Field(default={"type": "object", "properties": {}}, description="No parameters required")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            result = session.execute(
                select(Meeting)
                .options(
                    selectinload(Meeting.transcript),
                    selectinload(Meeting.summary)
                )
                .order_by(Meeting.created_at.desc())
                .limit(1)
            )
            meeting = result.scalars().first()

            if not meeting:
                return "No meetings found."

            header = f"Latest meeting: {meeting.title} (ID: {meeting.id}, Status: {meeting.status})\n"
            if meeting.summary and meeting.summary.text:
                return header + "\nSummary:\n" + meeting.summary.text
            if meeting.transcript and meeting.transcript.text:
                text = meeting.transcript.text
                snippet = text[:2000]
                suffix = "..." if len(text) > 2000 else ""
                return header + "\nTranscript snippet:\n" + snippet + suffix
            return header + "\nNo summary or transcript available yet."
        finally:
            session.close()


class SendFollowupEmailTool(BaseTool):
    name: str = "send_followup_email"
    description: str = "Send follow-up email with meeting summary to all participants. Requires meeting_id."
    meeting_id: int = Field(description="The ID of the meeting")
    subject: str = Field(default=None, description="Optional custom email subject")
    parameters: dict = Field(default={"type": "object", "properties": {"meeting_id": {"type": "integer", "description": "The ID of the meeting"}, "subject": {"type": "string", "description": "Optional custom email subject"}}, "required": ["meeting_id"]}, description="Tool parameters")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            result = session.execute(
                select(Summary).where(Summary.meeting_id == self.meeting_id)
            )
            summary = result.scalar_one_or_none()

            if not summary:
                return f"Meeting {self.meeting_id} must be summarized first."

            task = send_followup_task.delay(self.meeting_id, subject=self.subject)
            return f"Follow-up email being sent for meeting {self.meeting_id}. Task ID: {task.id}"
        finally:
            session.close()


class StartRecallMeetingTool(BaseTool):
    name: str = "start_recall_meeting"
    description: str = "Start a meeting by providing the Zoom/meeting link. Launches Recall and returns meeting ID."
    meeting_url: str = Field(description="The meeting URL (e.g., Zoom link)")
    title: str = Field(default=None, description="Optional meeting title")
    parameters: dict = Field(default={"type": "object", "properties": {"meeting_url": {"type": "string", "description": "The meeting URL (e.g., Zoom link)"}, "title": {"type": "string", "description": "Optional meeting title"}}, "required": ["meeting_url"]}, description="Tool parameters")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            meeting = Meeting(title=self.title or "Meeting")
            session.add(meeting)
            session.flush()

            try:
                data = await recall_service.start_bot(
                    meeting_url=self.meeting_url,
                    bot_name=(self.title or "Meeting Bot"),
                    external_id=str(meeting.id),
                )
                try:
                    bot_id = data.get("id") if isinstance(data, dict) else None
                    if bot_id:
                        r = redis.Redis.from_url(settings.redis_url)
                        r.set(f"recall:bot:{bot_id}", str(meeting.id))
                except Exception:
                    pass
                meeting.status = "recording"
                session.commit()
                return f"Meeting created and Recall started. ID: {meeting.id}"
            except Exception as e:
                session.rollback()
                return f"Failed to start Recall: {str(e)}"
        finally:
            session.close()


def get_meeting_tools():
    return [
        ListMeetingsTool(),
        GetMeetingDetailsTool(meeting_id=0),
        SendFollowupEmailTool(meeting_id=0),
        GetLastDiscussionTool(),
        StartRecallMeetingTool(meeting_url=""),
    ]


def create_meeting_agent():
    llm = ChatBot(
        model_name="openai/gpt-4.1",
        llm_provider="openrouter",
        llm_api_key=settings.openrouter_api_key,
    )
    agent = SpoonReactAI(
        llm=llm,
        tools=get_meeting_tools(),
        system_prompt="""You are a meeting assistant that helps users manage and recall meetings.

You can:
- Create a meeting by providing a Zoom/meeting link (starts Recall)
- List all meetings
- Get details of a specific meeting (transcript, summary, action items)
- Tell the user what was discussed last time (latest meeting summary or transcript)
- Send follow-up emails to participants

Always be helpful and concise. When a user asks about meetings, list them if no ID is specified. When they share a link, start a new meeting recording via Recall."""
    )
    return agent
