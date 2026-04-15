"""Handle /status command — check job progress."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from api_client import api_client

logger = logging.getLogger(__name__)

STATUS_EMOJI = {
    "queued": "🕐",
    "processing": "⏳",
    "completed": "✅",
    "failed": "❌",
}


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args or []

    if args:
        job_id = args[0]
    else:
        job_id = context.user_data.get("current_job_id")

    if not job_id:
        await update.message.reply_text(
            "ℹ️ *Usage:*  /status <job\\_id>\n\n"
            "You can also run a workflow first — the bot will remember your latest job.",
            parse_mode="Markdown",
        )
        return

    job = await api_client.get_job_status(str(job_id))
    if not job:
        await update.message.reply_text(
            f"⚠️ Could not find job `{job_id}`. It may not exist or the server is unreachable.",
            parse_mode="Markdown",
        )
        return

    status = job.get("status", "unknown")
    emoji = STATUS_EMOJI.get(status, "❓")
    wf_type = job.get("workflow_type", "unknown").replace("_", " ").title()
    created = job.get("created_at", "")[:19].replace("T", " ")

    lines = [
        f"{emoji} *Job Status*",
        f"",
        f"*ID:* `{job.get('id')}`",
        f"*Workflow:* {wf_type}",
        f"*Status:* {status}",
        f"*Created:* {created}",
    ]

    if job.get("started_at"):
        lines.append(f"*Started:* {job['started_at'][:19].replace('T', ' ')}")
    if job.get("completed_at"):
        lines.append(f"*Completed:* {job['completed_at'][:19].replace('T', ' ')}")
    if job.get("error_message"):
        lines.append(f"\n⚠️ *Error:* {job['error_message']}")

    if status == "completed":
        assets = await api_client.get_job_assets(str(job_id))
        if assets:
            lines.append(f"\n📦 *Assets:* {len(assets)} file(s) generated")
            for i, a in enumerate(assets, 1):
                url = a.get("file_url") or a.get("file_path", "")
                lines.append(f"  {i}. {a.get('asset_type', 'file')}: {url}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


def get_handlers() -> list[CommandHandler]:
    return [CommandHandler("status", status_command)]
