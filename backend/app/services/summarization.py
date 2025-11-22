import asyncio
from spoon_ai.agents import SpoonReactAI
from spoon_ai.chat import ChatBot
from app.config import settings


async def generate_meeting_summary(transcript_text: str) -> dict:
    agent = SpoonReactAI(
        llm=ChatBot(
            model_name="openai/gpt-4.1",
            llm_provider="openrouter",
            llm_api_key=settings.openrouter_api_key,
        )
    )

    prompt = f"""Analyze the following meeting transcript and provide:
1. A concise summary (2-3 paragraphs)
2. A list of action items with assignees (if mentioned)
3. Key decisions made during the meeting

Format your response as JSON with the following structure:
{{
    "summary": "...",
    "action_items": [
        {{"task": "...", "assignee": "...", "deadline": "..."}}
    ],
    "decisions": ["...", "..."]
}}

Transcript:
{transcript_text}
"""

    response = await agent.run(prompt)

    import json
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        result = {
            "summary": response,
            "action_items": [],
            "decisions": []
        }

    return result


def generate_meeting_summary_sync(transcript_text: str) -> dict:
    return asyncio.run(generate_meeting_summary(transcript_text))
