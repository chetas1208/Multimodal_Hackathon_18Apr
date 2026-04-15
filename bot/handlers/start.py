from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from api_client import api_client

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "🎬 *Marketing Studio Bot*\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "Your AI-powered marketing studio, right here in Telegram.\n"
    "Create scroll-stopping video ads and short-form clips in minutes.\n\n"
    "*Available commands:*\n\n"
    "/generate — Create a promotional video ad from your product\n"
    "/clip — Turn a long video into short, viral clips\n"
    "/status — Check the status of a running job\n"
    "/help — Show this help message\n\n"
    "_Send /generate or /clip to get started!_"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return

    result = await api_client.create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
    )
    if result:
        context.user_data["backend_user_id"] = result.get("id")
        logger.info("Registered/fetched user %s (backend id: %s)", user.id, result.get("id"))

    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(WELCOME_TEXT, parse_mode="Markdown")


def get_handlers() -> list[CommandHandler]:
    return [
        CommandHandler("start", start_command),
        CommandHandler("help", help_command),
    ]
