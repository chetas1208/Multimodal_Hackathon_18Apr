from __future__ import annotations

from pydantic import BaseModel

from app.models.bot_session import WorkflowType


class TelegramUser(BaseModel):
    id: int
    is_bot: bool = False
    first_name: str = ""
    username: str | None = None


class TelegramChat(BaseModel):
    id: int
    type: str = "private"


class TelegramMessage(BaseModel):
    message_id: int
    from_: TelegramUser | None = None
    chat: TelegramChat
    text: str | None = None
    date: int = 0

    class Config:
        populate_by_name = True

    model_config = {"populate_by_name": True}


class TelegramWebhookPayload(BaseModel):
    update_id: int
    message: TelegramMessage | None = None


class BotMessage(BaseModel):
    chat_id: int
    text: str
    parse_mode: str | None = "Markdown"


class WorkflowStartRequest(BaseModel):
    telegram_id: int
    workflow_type: WorkflowType
    product_url: str | None = None
    product_text: str | None = None
    youtube_url: str | None = None
