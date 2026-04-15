"""Workflow B: Clip a long video into short-form clips."""

from __future__ import annotations

import asyncio
import logging
import re
from io import BytesIO

import httpx
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from api_client import api_client
from config import settings

logger = logging.getLogger(__name__)

WAITING_SOURCE, PROCESSING = range(2)

YOUTUBE_PATTERN = re.compile(
    r"(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)[\w\-]+"
)


async def clip_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["clip_source"] = None

    await update.message.reply_text(
        "✂️ *Let's clip your video into shorts!*\n\n"
        "Send me one of the following:\n"
        "• A *YouTube URL* (full video or shorts link)\n"
        "• A *video file* (upload directly)\n",
        parse_mode="Markdown",
    )
    return WAITING_SOURCE


async def receive_url_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text or ""
    if not YOUTUBE_PATTERN.search(text) and not text.strip().startswith("http"):
        await update.message.reply_text(
            "That doesn't look like a valid YouTube URL. "
            "Please send a YouTube link or upload a video file directly."
        )
        return WAITING_SOURCE

    context.user_data["clip_source"] = {"type": "url", "value": text.strip()}

    await update.message.reply_text(
        f"✅ Got your video link!\n\n"
        f"⏳ *Analyzing and clipping your video...* This may take a few minutes.",
        parse_mode="Markdown",
    )
    return await _process_clip(update, context)


async def receive_video_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    video = update.message.video or update.message.document
    if video is None:
        await update.message.reply_text("Please send a video file or a YouTube URL.")
        return WAITING_SOURCE

    await update.message.reply_text("📤 Uploading your video...")

    file = await video.get_file()
    buf = BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)

    filename = getattr(video, "file_name", None) or "uploaded_video.mp4"
    uploaded = await api_client.upload_file(buf.read(), filename)

    if not uploaded:
        await update.message.reply_text("⚠️ Failed to upload the video. Please try again.")
        return WAITING_SOURCE

    context.user_data["clip_source"] = {
        "type": "file",
        "value": uploaded.get("url") or uploaded.get("file_path", ""),
        "filename": filename,
    }

    await update.message.reply_text(
        "✅ Video uploaded!\n\n"
        "⏳ *Analyzing and clipping your video...* This may take a few minutes.",
        parse_mode="Markdown",
    )
    return await _process_clip(update, context)


async def _process_clip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data.get("backend_user_id")
    if not user_id:
        user = update.effective_user
        result = await api_client.create_user(user.id, user.username, user.first_name)
        if result:
            user_id = result.get("id")
            context.user_data["backend_user_id"] = user_id

    if not user_id:
        await update.message.reply_text("❌ Could not authenticate. Please try /start first.")
        return ConversationHandler.END

    source = context.user_data.get("clip_source", {})
    input_data = {}
    if source.get("type") == "url":
        input_data["youtube_url"] = source["value"]
    else:
        input_data["video_file"] = source.get("value", "")
        input_data["filename"] = source.get("filename", "")

    job = await api_client.create_job(
        user_id=user_id,
        workflow_type="clip_shorts",
        input_data=input_data,
    )

    if not job:
        await update.message.reply_text(
            "❌ Failed to create the clipping job. The server might be down."
        )
        return ConversationHandler.END

    job_id = job.get("id")
    context.user_data["current_job_id"] = job_id
    logger.info("Created clip_shorts job %s", job_id)

    completed = await _poll_job(job_id, update)

    if completed and completed.get("status") == "completed":
        await _send_clip_results(update, context, job_id, completed)
    elif completed and completed.get("status") == "failed":
        error = completed.get("error_message", "Unknown error")
        await update.message.reply_text(f"❌ Clipping failed: {error}")
    else:
        await update.message.reply_text(
            f"⏱️ Still processing. Check status with:\n/status {job_id}"
        )

    return ConversationHandler.END


async def _poll_job(job_id: str, update: Update) -> dict | None:
    elapsed = 0.0
    interval = settings.POLL_INTERVAL
    timeout = settings.POLL_TIMEOUT

    while elapsed < timeout:
        await asyncio.sleep(interval)
        elapsed += interval

        status = await api_client.get_job_status(job_id)
        if not status:
            continue

        current = status.get("status")
        if current in ("completed", "failed"):
            return status

        if elapsed % 15 < interval:
            await update.message.reply_text("⏳ Still analyzing your video...")

    return await api_client.get_job_status(job_id)


async def _send_clip_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    job_id: str,
    job_data: dict,
) -> None:
    assets = await api_client.get_job_assets(job_id) or []
    output = job_data.get("output_data") or {}

    await update.message.reply_text(
        f"✂️ *Clipping complete!* Found *{len(assets)}* clips.\n"
        "Here they are, ranked by engagement potential:",
        parse_mode="Markdown",
    )

    clip_analyses = output.get("clips", [])

    for idx, asset in enumerate(assets):
        file_url = asset.get("file_url") or asset.get("file_path")
        if not file_url:
            continue

        analysis = clip_analyses[idx] if idx < len(clip_analyses) else {}
        engagement = analysis.get("engagement_score", asset.get("metadata", {}).get("engagement_score", "N/A"))
        reason = analysis.get("selection_reason", asset.get("metadata", {}).get("clip_selection_reason", ""))
        duration = asset.get("duration")

        caption_lines = [f"🎬 *Clip {idx + 1}*"]
        if duration:
            caption_lines.append(f"⏱️ Duration: {duration:.1f}s")
        if engagement != "N/A":
            score_val = float(engagement) if isinstance(engagement, (int, float)) else 0
            bar = "█" * int(score_val * 10) + "░" * (10 - int(score_val * 10))
            caption_lines.append(f"📊 Engagement: {bar} {score_val:.1f}/1.0")
        if reason:
            caption_lines.append(f"💡 Why: {reason}")

        caption = "\n".join(caption_lines)

        if file_url.startswith("http"):
            try:
                async with httpx.AsyncClient() as dl:
                    resp = await dl.get(file_url, timeout=60.0)
                    resp.raise_for_status()
                    await update.message.reply_video(
                        video=BytesIO(resp.content),
                        filename=f"clip_{idx+1}.mp4",
                        caption=caption,
                        parse_mode="Markdown",
                    )
            except Exception as exc:
                logger.error("Failed to send clip %d: %s", idx + 1, exc)
                await update.message.reply_text(f"📎 Clip {idx+1}: {file_url}\n{caption}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"📎 Clip {idx+1}: {file_url}\n{caption}", parse_mode="Markdown")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("clip_source", None)
    await update.message.reply_text("❌ Clipping cancelled. Send /clip to start over.")
    return ConversationHandler.END


def get_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("clip", clip_entry)],
        states={
            WAITING_SOURCE: [
                MessageHandler(filters.VIDEO | filters.Document.VIDEO, receive_video_source),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url_source),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
