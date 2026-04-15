from __future__ import annotations

import logging
import os
import subprocess
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class ClipExtractorService:
    """Extract short clips from a longer video based on transcript segments.

    In production, this would use ML-based scene detection and hook analysis.
    For demo, it segments the video at transcript boundaries using ffmpeg.
    """

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or os.path.join(settings.STORAGE_LOCAL_PATH, "clips")
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_clips(
        self,
        video_path: str,
        transcript: dict,
        max_clips: int = 5,
        target_duration: float = 30.0,
    ) -> list[dict]:
        segments = transcript.get("segments", [])
        if not segments:
            return self._mock_clips(max_clips)

        clips: list[dict] = []
        current_start = segments[0].get("start", 0.0)
        accumulated_text = ""

        for seg in segments:
            accumulated_text += " " + seg.get("text", "")
            seg_end = seg.get("end", seg.get("start", 0) + target_duration)

            if (seg_end - current_start) >= target_duration or seg == segments[-1]:
                clip_path = self._cut_clip(video_path, current_start, seg_end)
                clips.append({
                    "start": round(current_start, 2),
                    "end": round(seg_end, 2),
                    "duration": round(seg_end - current_start, 2),
                    "text": accumulated_text.strip(),
                    "file_path": clip_path,
                    "score": min(95.0, 60 + len(accumulated_text.split()) * 0.5),
                })
                current_start = seg_end
                accumulated_text = ""

                if len(clips) >= max_clips:
                    break

        return clips or self._mock_clips(max_clips)

    def _cut_clip(self, video_path: str, start: float, end: float) -> str:
        output_path = os.path.join(self.output_dir, f"{uuid.uuid4().hex}_clip.mp4")

        if not os.path.isfile(video_path):
            logger.warning("Source video not found: %s, returning mock", video_path)
            with open(output_path, "wb") as f:
                f.write(b"\x00" * 512)
            return output_path

        try:
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start),
                "-to", str(end),
                "-i", video_path,
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                output_path,
            ]
            subprocess.run(cmd, capture_output=True, timeout=120, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.warning("ffmpeg clip cut failed (%s), creating placeholder", exc)
            with open(output_path, "wb") as f:
                f.write(b"\x00" * 512)

        return output_path

    def _mock_clips(self, count: int) -> list[dict]:
        mock_texts = [
            "This product changed my morning routine completely",
            "Here's what nobody tells you about skincare",
            "Wait until you see the before and after",
            "I've been using this for 30 days and the results speak for themselves",
            "Stop scrolling — you need to see this",
        ]
        clips = []
        for i in range(min(count, len(mock_texts))):
            clip_path = os.path.join(self.output_dir, f"{uuid.uuid4().hex}_mock_clip.mp4")
            with open(clip_path, "wb") as f:
                f.write(b"\x00" * 512)
            clips.append({
                "start": i * 30.0,
                "end": (i + 1) * 30.0,
                "duration": 30.0,
                "text": mock_texts[i],
                "file_path": clip_path,
                "score": round(85 - i * 3.5, 1),
            })
        return clips
