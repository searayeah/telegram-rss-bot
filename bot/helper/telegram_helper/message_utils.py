from telegram import Update
from telegram.constants import MessageLimit
from telegram.ext import ContextTypes

from bot import TELEGRAM_CHAT_ID


async def reply_text_with_chunks(update: Update, response: str, **kwargs) -> None:
    while len(response) > MessageLimit.MAX_TEXT_LENGTH:
        split_point = response.rfind("\n", 0, MessageLimit.MAX_TEXT_LENGTH)
        if split_point == -1:
            split_point = MessageLimit.MAX_TEXT_LENGTH
        chunk = response[:split_point]
        await update.message.reply_text(
            chunk,
            **kwargs,
        )
        response = response[split_point:].lstrip()
    if response:
        await update.message.reply_text(
            response,
            **kwargs,
        )


async def send_text_with_chunks(
    context: ContextTypes.DEFAULT_TYPE, message: str, **kwargs
) -> None:
    while len(message) > MessageLimit.MAX_TEXT_LENGTH:
        split_point = message.rfind("\n", 0, MessageLimit.MAX_TEXT_LENGTH)
        if split_point == -1:
            split_point = MessageLimit.MAX_TEXT_LENGTH
        chunk = message[:split_point]
        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=chunk,
            **kwargs,
        )
        message = message[split_point:].lstrip()
    if message:
        await context.bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            **kwargs,
        )
