from __future__ import annotations

import logging
import os
import subprocess
import uuid

from app.config import settings

logger = logging.getLogger(__name__)


class VideoGeneratorService:
    """Mock video generation service.

    In production, this would call a real ML pipeline (e.g., Runway, Pika,
    or a custom diffusion model). For demo purposes it creates a simple
    coloured-frame video with text overlays using ffmpeg.
    """

    def __init__(self, output_dir: str | None = None):
        self.output_dir = output_dir or os.path.join(settings.STORAGE_LOCAL_PATH, "generated")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_promo_video(
        self,
        images: list[str] | None = None,
        text: str = "Your Product",
        product_url: str = "",
        duration: int = 10,
    ) -> str:
        output_path = os.path.join(self.output_dir, f"{uuid.uuid4().hex}_promo.mp4")

        try:
            subtitle_text = text[:60].replace("'", "")
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", f"color=c=0x1a1a2e:s=1080x1920:d={duration}:r=30",
                "-f", "lavfi",
                "-i", f"sine=frequency=440:duration={duration}",
                "-vf", (
                    f"drawtext=text='{subtitle_text}'"
                    ":fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2"
                    ":borderw=2:bordercolor=black,"
                    "drawtext=text='Marketing Studio Bot'"
                    ":fontcolor=0x6c63ff:fontsize=32:x=(w-text_w)/2:y=100"
                    ":borderw=1:bordercolor=black"
                ),
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-shortest",
                output_path,
            ]
            subprocess.run(cmd, capture_output=True, timeout=60, check=True)
            logger.info("Generated promo video: %s", output_path)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.warning("ffmpeg failed (%s), returning mock path", exc)
            output_path = self._create_mock_path("promo")

        return output_path

    def _create_mock_path(self, label: str) -> str:
        mock_path = os.path.join(self.output_dir, f"{uuid.uuid4().hex}_{label}_mock.mp4")
        with open(mock_path, "wb") as f:
            f.write(b"\x00" * 1024)
        return mock_path
