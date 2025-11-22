from spoon_ai.agents import SpoonReactAI
from spoon_ai.chat import ChatBot
from spoon_ai.tools import BaseTool
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.meeting import Meeting, Transcript, Summary, Participant
from app.tasks.transcription import get_sync_session, transcribe_audio_task
from app.tasks.summarization import generate_summary_task
from app.tasks.email import send_followup_task


class ListMeetingsTool(BaseTool):
    name: str = "list_meetings"
    description: str = "List all meetings with their status. Returns meeting id, title, date, and status."
    parameters: dict = Field(default_factory=dict, description="No parameters required")

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
    parameters: dict = Field(default_factory=dict, description="Tool parameters")

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


class StartTranscriptionTool(BaseTool):
    name: str = "start_transcription"
    description: str = "Start transcription process for a meeting. Requires meeting_id. This is an async task."
    meeting_id: int = Field(description="The ID of the meeting to transcribe")
    parameters: dict = Field(default_factory=dict, description="Tool parameters")

    async def execute(self) -> str:
        task = transcribe_audio_task.delay(self.meeting_id)
        return f"Transcription started for meeting {self.meeting_id}. Task ID: {task.id}"


class StartSummarizationTool(BaseTool):
    name: str = "start_summarization"
    description: str = "Generate summary for a transcribed meeting. Requires meeting_id. Meeting must be transcribed first."
    meeting_id: int = Field(description="The ID of the meeting to summarize")
    parameters: dict = Field(default_factory=dict, description="Tool parameters")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            result = session.execute(
                select(Transcript).where(Transcript.meeting_id == self.meeting_id)
            )
            transcript = result.scalar_one_or_none()

            if not transcript:
                return f"Meeting {self.meeting_id} must be transcribed first."

            task = generate_summary_task.delay(self.meeting_id)
            return f"Summarization started for meeting {self.meeting_id}. Task ID: {task.id}"
        finally:
            session.close()


class SendFollowupEmailTool(BaseTool):
    name: str = "send_followup_email"
    description: str = "Send follow-up email with meeting summary to all participants. Requires meeting_id."
    meeting_id: int = Field(description="The ID of the meeting")
    subject: str = Field(default=None, description="Optional custom email subject")
    parameters: dict = Field(default_factory=dict, description="Tool parameters")

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


class CreateMeetingTool(BaseTool):
    name: str = "create_meeting"
    description: str = "Create a new meeting with audio URL. Returns the meeting ID."
    title: str = Field(description="Title of the meeting")
    audio_url: str = Field(description="URL to the audio file")
    participant_names: str = Field(default="", description="Comma-separated list of participant names")
    participant_emails: str = Field(default="", description="Comma-separated list of participant emails")
    parameters: dict = Field(default_factory=dict, description="Tool parameters")

    async def execute(self) -> str:
        session = get_sync_session()
        try:
            meeting = Meeting(title=self.title, audio_url=self.audio_url)
            session.add(meeting)
            session.flush()

            names = [n.strip() for n in self.participant_names.split(",") if n.strip()]
            emails = [e.strip() for e in self.participant_emails.split(",") if e.strip()]

            for name, email in zip(names, emails):
                participant = Participant(meeting_id=meeting.id, name=name, email=email)
                session.add(participant)

            session.commit()
            return f"Meeting created with ID: {meeting.id}"
        finally:
            session.close()


def get_meeting_tools():
    return [
        ListMeetingsTool(),
        GetMeetingDetailsTool(meeting_id=0),
        StartTranscriptionTool(meeting_id=0),
        StartSummarizationTool(meeting_id=0),
        SendFollowupEmailTool(meeting_id=0),
        CreateMeetingTool(title="", audio_url=""),
    ]


def create_meeting_agent():
    llm = ChatBot(
        model_name="openai/gpt-3.5-turbo",
        llm_provider="openrouter",
        llm_api_key=settings.openrouter_api_key,
    )
    agent = SpoonReactAI(
        llm=llm,
        tools=get_meeting_tools(),
        system_prompt="""You are a meeting assistant that helps users manage their meetings, transcriptions, and summaries.

You can:
- List all meetings
- Get details of a specific meeting (transcript, summary, action items)
- Start transcription for a meeting
- Generate summaries from transcripts
- Send follow-up emails to participants

Always be helpful and concise. When a user asks about meetings, first list them if they don't specify an ID.
When they want to process a meeting, guide them through: transcribe -> summarize -> send follow-up."""
    )
    return agent
