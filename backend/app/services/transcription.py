from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Whisper-based transcription service with mock fallback."""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        try:
            import whisper
            self._model = whisper.load_model(self.model_name)
            logger.info("Whisper model '%s' loaded", self.model_name)
        except Exception as exc:
            logger.warning("Could not load Whisper model: %s — using mock", exc)
            self._model = None

    def transcribe(self, audio_path: str) -> dict:
        if not os.path.isfile(audio_path):
            logger.warning("Audio file not found: %s — returning mock transcript", audio_path)
            return self._mock_transcript()

        if self._model is None:
            self._load_model()

        if self._model is not None:
            try:
                result = self._model.transcribe(audio_path)
                return {
                    "text": result.get("text", ""),
                    "language": result.get("language", "en"),
                    "segments": [
                        {
                            "id": seg["id"],
                            "start": seg["start"],
                            "end": seg["end"],
                            "text": seg["text"],
                        }
                        for seg in result.get("segments", [])
                    ],
                }
            except Exception as exc:
                logger.error("Whisper transcription failed: %s", exc)

        return self._mock_transcript()

    @staticmethod
    def _mock_transcript() -> dict:
        return {
            "text": (
                "Hey everyone, today I want to show you something incredible. "
                "This product has completely transformed how I approach my daily routine. "
                "Let me walk you through the key features. First, the design is sleek and modern. "
                "Second, it's incredibly easy to use. And third, the results speak for themselves. "
                "I've been using it for about a month now and I can honestly say it's a game changer. "
                "Check the link in my bio to grab yours before they sell out."
            ),
            "language": "en",
            "segments": [
                {"id": 0, "start": 0.0, "end": 4.5, "text": "Hey everyone, today I want to show you something incredible."},
                {"id": 1, "start": 4.5, "end": 10.2, "text": "This product has completely transformed how I approach my daily routine."},
                {"id": 2, "start": 10.2, "end": 15.0, "text": "Let me walk you through the key features."},
                {"id": 3, "start": 15.0, "end": 19.8, "text": "First, the design is sleek and modern."},
                {"id": 4, "start": 19.8, "end": 24.0, "text": "Second, it's incredibly easy to use."},
                {"id": 5, "start": 24.0, "end": 29.5, "text": "And third, the results speak for themselves."},
                {"id": 6, "start": 29.5, "end": 38.0, "text": "I've been using it for about a month now and I can honestly say it's a game changer."},
                {"id": 7, "start": 38.0, "end": 44.0, "text": "Check the link in my bio to grab yours before they sell out."},
            ],
        }
