"""Real-time transcription service for streaming audio from Zoom meetings."""

import asyncio
import json
from typing import AsyncGenerator, Callable, Optional
from datetime import datetime

import openai

from app.config import settings


class StreamingTranscriptionService:
    """Service for transcribing real-time audio streams using OpenAI Whisper."""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.whisper_model

    async def transcribe_stream(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        on_transcript: Callable[[str, dict], None],
        language: Optional[str] = None,
    ) -> str:
        """Transcribe a real-time audio stream.

        Args:
            audio_stream: Async generator yielding audio chunks (PCM format)
            on_transcript: Callback function called for each transcription segment
                          Signature: on_transcript(text: str, metadata: dict)
            language: Optional language code (e.g., 'en', 'es')

        Returns:
            Full transcript text
        """
        full_transcript = ""
        buffer = b""
        min_chunk_size = 4096  # Minimum audio chunk size for whisper

        async for chunk in audio_stream:
            buffer += chunk

            # Process buffer when it reaches minimum size
            if len(buffer) >= min_chunk_size:
                try:
                    transcript_data = await self._transcribe_audio_chunk(
                        buffer, language
                    )

                    if transcript_data and transcript_data.get("text"):
                        text = transcript_data["text"].strip()
                        if text:
                            full_transcript += " " + text
                            # Call callback with transcribed segment
                            metadata = {
                                "timestamp": datetime.utcnow().isoformat(),
                                "confidence": transcript_data.get("confidence"),
                            }
                            on_transcript(text, metadata)

                    buffer = b""
                except Exception as e:
                    print(f"Error transcribing audio chunk: {e}")
                    # Clear buffer on error to continue processing
                    buffer = b""

        # Process remaining buffer
        if buffer:
            try:
                transcript_data = await self._transcribe_audio_chunk(
                    buffer, language
                )
                if transcript_data and transcript_data.get("text"):
                    text = transcript_data["text"].strip()
                    if text:
                        full_transcript += " " + text
                        metadata = {
                            "timestamp": datetime.utcnow().isoformat(),
                            "confidence": transcript_data.get("confidence"),
                        }
                        on_transcript(text, metadata)
            except Exception as e:
                print(f"Error transcribing final audio chunk: {e}")

        return full_transcript.strip()

    async def _transcribe_audio_chunk(
        self, audio_data: bytes, language: Optional[str] = None
    ) -> dict:
        """Transcribe a single audio chunk using OpenAI Whisper API.

        Args:
            audio_data: Raw audio bytes (PCM format)
            language: Optional language code

        Returns:
            Transcription data with 'text' and 'confidence' keys
        """
        # Note: In production, you'd want to handle audio format conversion
        # and proper API interactions with Whisper
        try:
            # This is a placeholder for actual Whisper API call
            # You may need to adjust based on your actual API usage
            result = await asyncio.to_thread(
                lambda: self._sync_transcribe(audio_data, language)
            )
            return result
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return {"text": "", "confidence": 0}

    def _sync_transcribe(self, audio_data: bytes, language: Optional[str]) -> dict:
        """Synchronous wrapper for Whisper transcription."""
        # This would be implemented with actual Whisper model loading
        # For now, returning empty transcription as placeholder
        return {"text": "", "confidence": 0.0}


streaming_transcription_service = StreamingTranscriptionService()
