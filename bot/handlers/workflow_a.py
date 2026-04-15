"""Workflow A: Generate a promotional video ad from product details."""

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

WAITING_URL, WAITING_IMAGES, WAITING_TEXT, PROCESSING = range(4)

URL_PATTERN = re.compile(r"https?://\S+")


async def generate_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["product_images"] = []
    context.user_data["product_url"] = None
    context.user_data["product_text"] = None

    await update.message.reply_text(
        "🛍️ *Let's create a video ad!*\n\n"
        "First, send me your *product URL* (e.g. a Shopify, Amazon, or any product page).",
        parse_mode="Markdown",
    )
    return WAITING_URL


async def receive_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text or ""
    if not URL_PATTERN.search(text):
        await update.message.reply_text(
            "That doesn't look like a valid URL. Please send a link starting with http:// or https://."
        )
        return WAITING_URL

    context.user_data["product_url"] = text.strip()
    await update.message.reply_text(
        "✅ Got your product URL!\n\n"
        "Now send me *1–5 product images*. Send them as photos one by one.\n"
        "When you're done uploading images, type /done or send your product description.",
        parse_mode="Markdown",
    )
    return WAITING_IMAGES


async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    images: list[str] = context.user_data.get("product_images", [])

    if len(images) >= 5:
        await update.message.reply_text(
            "You've already sent 5 images (the maximum). "
            "Type /done or send your product description to continue."
        )
        return WAITING_IMAGES

    photo = update.message.photo[-1]
    file = await photo.get_file()
    buf = BytesIO()
    await file.download_to_memory(buf)
    buf.seek(0)

    uploaded = await api_client.upload_file(buf.read(), f"product_{len(images)+1}.jpg")
    if uploaded:
        images.append(uploaded.get("url") or uploaded.get("file_path", ""))
        context.user_data["product_images"] = images
        count = len(images)
        if count < 5:
            await update.message.reply_text(
                f"📸 Image {count}/5 received! Send more or type /done."
            )
        else:
            await update.message.reply_text(
                "📸 5/5 images received (maximum reached).\n\n"
                "Now *describe your product* in a few sentences — what it does, who it's for, "
                "and any key selling points.",
                parse_mode="Markdown",
            )
            return WAITING_TEXT
    else:
        await update.message.reply_text("⚠️ Failed to upload that image. Please try again.")

    return WAITING_IMAGES


async def images_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    images = context.user_data.get("product_images", [])
    if not images:
        await update.message.reply_text(
            "You haven't sent any images yet. Please send at least one product photo."
        )
        return WAITING_IMAGES

    await update.message.reply_text(
        f"✅ {len(images)} image(s) received!\n\n"
        "Now *describe your product* in a few sentences — what it does, who it's for, "
        "and any key selling points.",
        parse_mode="Markdown",
    )
    return WAITING_TEXT


async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text or ""
    if len(text.strip()) < 10:
        await update.message.reply_text(
            "Please provide a more detailed description (at least a couple of sentences)."
        )
        return WAITING_TEXT

    context.user_data["product_text"] = text.strip()
    url = context.user_data.get("product_url", "N/A")
    count = len(context.user_data.get("product_images", []))

    await update.message.reply_text(
        "📋 *Here's what I've got:*\n\n"
        f"🔗 URL: {url}\n"
        f"🖼️ Images: {count}\n"
        f"📝 Description: _{text[:120]}{'...' if len(text) > 120 else ''}_\n\n"
        "⏳ *Processing your video ad...* This may take a few minutes.",
        parse_mode="Markdown",
    )
    return await _process_generate(update, context)


async def _process_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = context.user_data.get("backend_user_id")
    if not user_id:
        user = update.effective_user
        result = await api_client.create_user(user.id, user.username, user.first_name)
        if result:
            user_id = result.get("id")
            context.user_data["backend_user_id"] = user_id

    if not user_id:
        await update.message.reply_text("❌ Could not authenticate with the server. Please try /start again.")
        return ConversationHandler.END

    job = await api_client.create_job(
        user_id=user_id,
        workflow_type="generate_video",
        input_data={
            "product_url": context.user_data.get("product_url"),
            "product_images": context.user_data.get("product_images", []),
            "product_text": context.user_data.get("product_text"),
        },
    )

    if not job:
        await update.message.reply_text(
            "❌ Failed to create the job. The server might be down. Please try again later."
        )
        return ConversationHandler.END

    job_id = job.get("id")
    context.user_data["current_job_id"] = job_id
    logger.info("Created generate_video job %s", job_id)

    completed = await _poll_job(job_id, update)

    if completed and completed.get("status") == "completed":
        await _send_generate_results(update, context, job_id, completed)
    elif completed and completed.get("status") == "failed":
        error = completed.get("error_message", "Unknown error")
        await update.message.reply_text(f"❌ Job failed: {error}")
    else:
        await update.message.reply_text(
            f"⏱️ Job is still processing. Check back with:\n/status {job_id}"
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
            await update.message.reply_text("⏳ Still working on your video...")

    return await api_client.get_job_status(job_id)


async def _send_generate_results(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    job_id: str,
    job_data: dict,
) -> None:
    assets = await api_client.get_job_assets(job_id) or []

    output = job_data.get("output_data") or {}
    summary_parts = ["🎬 *Your video ad is ready!*\n"]

    scores = output.get("analysis", {})
    if scores:
        summary_parts.append("📊 *Analysis Scores:*")
        for label, key in [
            ("Hook", "hook_score"),
            ("CTA", "cta_score"),
            ("Pacing", "pacing_score"),
            ("Platform Fit", "platform_fit_score"),
            ("Engagement", "engagement_score"),
        ]:
            val = scores.get(key)
            if val is not None:
                bar = "█" * int(float(val) * 10) + "░" * (10 - int(float(val) * 10))
                summary_parts.append(f"  {label}: {bar} {float(val):.1f}/1.0")

    explanation = output.get("explanation") or scores.get("explanation")
    if explanation:
        summary_parts.append(f"\n💡 *Insights:* {explanation}")

    await update.message.reply_text("\n".join(summary_parts), parse_mode="Markdown")

    for asset in assets:
        file_url = asset.get("file_url") or asset.get("file_path")
        if not file_url:
            continue
        asset_type = asset.get("asset_type", "")
        if asset_type == "video" and file_url.startswith("http"):
            try:
                async with httpx.AsyncClient() as dl:
                    resp = await dl.get(file_url, timeout=60.0)
                    resp.raise_for_status()
                    await update.message.reply_video(
                        video=BytesIO(resp.content),
                        filename="marketing_video.mp4",
                        caption="🎬 Your generated video ad",
                    )
            except Exception as exc:
                logger.error("Failed to send video: %s", exc)
                await update.message.reply_text(f"📎 Video download link: {file_url}")
        elif file_url.startswith("http"):
            await update.message.reply_text(f"📎 Asset: {file_url}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.pop("product_images", None)
    context.user_data.pop("product_url", None)
    context.user_data.pop("product_text", None)
    await update.message.reply_text("❌ Video generation cancelled. Send /generate to start over.")
    return ConversationHandler.END


def get_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("generate", generate_entry)],
        states={
            WAITING_URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_url),
            ],
            WAITING_IMAGES: [
                MessageHandler(filters.PHOTO, receive_image),
                CommandHandler("done", images_done),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text),
            ],
            WAITING_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True,
    )
