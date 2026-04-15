"""Marketing Studio Bot — Telegram entry point."""

from __future__ import annotations

import argparse
import logging
import sys

from telegram.ext import Application

from api_client import api_client
from config import settings
from handlers import start, status, workflow_a, workflow_b

logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def build_app() -> Application:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set. Exiting.")
        sys.exit(1)

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    for handler in start.get_handlers():
        app.add_handler(handler)

    app.add_handler(workflow_a.get_handler())
    app.add_handler(workflow_b.get_handler())

    for handler in status.get_handlers():
        app.add_handler(handler)

    return app


async def on_shutdown(app: Application) -> None:
    logger.info("Shutting down — closing API client...")
    await api_client.close()


def run_polling(app: Application) -> None:
    logger.info("Starting bot in POLLING mode...")
    app.post_shutdown = on_shutdown
    app.run_polling(drop_pending_updates=True)


def run_webhook(app: Application) -> None:
    if not settings.WEBHOOK_URL:
        logger.error("WEBHOOK_URL is required for webhook mode. Exiting.")
        sys.exit(1)

    webhook_path = "/bot/webhook"
    full_url = settings.WEBHOOK_URL.rstrip("/") + webhook_path

    logger.info("Starting bot in WEBHOOK mode at %s", full_url)
    app.post_shutdown = on_shutdown
    app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=webhook_path,
        webhook_url=full_url,
        drop_pending_updates=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Marketing Studio Telegram Bot")
    parser.add_argument(
        "--mode",
        choices=["polling", "webhook"],
        default="polling",
        help="Run mode: polling (dev) or webhook (prod). Default: polling",
    )
    args = parser.parse_args()

    app = build_app()

    if args.mode == "webhook":
        run_webhook(app)
    else:
        run_polling(app)


if __name__ == "__main__":
    main()
