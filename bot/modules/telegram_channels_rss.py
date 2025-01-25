from telegram.ext import CommandHandler, filters

from bot import CHANNEL_URLS, FILTER_WORDS, TELEGRAM_CHAT_ID, UPDATE_TIME, application
from bot.helper.telegram_channels_rss_parser import (
    get_channel_name_from_url,
    get_new_filtered_telegram_channel_posts,
    sanitize_html,
)

channels = [get_channel_name_from_url(channel_url) for channel_url in CHANNEL_URLS]
current_channel_name_to_ids = {channel_name: {} for channel_name in channels}


async def send_updates(send_func, **kwargs):
    for channel_name in channels:
        title, id_to_post = await get_new_filtered_telegram_channel_posts(
            channel_name, current_channel_name_to_ids[channel_name], FILTER_WORDS
        )
        if id_to_post:
            for id in id_to_post:
                html_text = (
                    f"<b>{title}</b>\n\n"
                    + sanitize_html(id_to_post[id])["text"]
                    + f"\n\n{id}"
                )
                await send_func(text=html_text, **kwargs)
            current_channel_name_to_ids[channel_name] = id_to_post


async def get_updates(update, context):
    await send_updates(
        update.message.reply_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


async def check_updates(context):
    await send_updates(
        context.bot.send_message,
        chat_id=TELEGRAM_CHAT_ID,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


application.add_handler(
    CommandHandler("get", get_updates, filters=filters.User(int(TELEGRAM_CHAT_ID)))
)

application.job_queue.run_repeating(check_updates, interval=UPDATE_TIME, first=10)
