from __future__ import annotations

import logging
import os
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class YouTubeService:
    """Download YouTube videos using yt-dlp with a mock fallback."""

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or os.path.join(settings.STORAGE_LOCAL_PATH, "youtube")
        os.makedirs(self.output_dir, exist_ok=True)

    def download_video(self, url: str, max_duration: int = 600) -> str:
        output_path = os.path.join(self.output_dir, f"{uuid.uuid4().hex}.mp4")

        try:
            import yt_dlp

            ydl_opts = {
                "outtmpl": output_path,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "match_filter": lambda info, *_: (
                    "Video too long" if info.get("duration", 0) > max_duration else None
                ),
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.isfile(output_path):
                logger.info("Downloaded YouTube video: %s -> %s", url, output_path)
                return output_path

        except Exception as exc:
            logger.warning("yt-dlp download failed (%s), returning mock", exc)

        return self._create_mock(url)

    def _create_mock(self, url: str) -> str:
        mock_path = os.path.join(self.output_dir, f"{uuid.uuid4().hex}_mock_yt.mp4")
        with open(mock_path, "wb") as f:
            f.write(b"\x00" * 2048)
        logger.info("Created mock YouTube download: %s", mock_path)
        return mock_path

    @staticmethod
    def extract_video_id(url: str) -> str | None:
        import re

        patterns = [
            r"(?:v=|\/v\/|youtu\.be\/)([a-zA-Z0-9_-]{11})",
            r"(?:shorts\/)([a-zA-Z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
