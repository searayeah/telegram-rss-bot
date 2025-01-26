from dataclasses import asdict
from datetime import datetime, timedelta

from loguru import logger
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, filters
from telegram.helpers import escape_markdown

from bot import REDDIT_SUBREDDITS, TELEGRAM_CHAT_ID, application
from bot.helper.ext_utils.db_handler import database
from bot.helper.ext_utils.ollama import summarize
from bot.helper.reddit_rss_parser import (
    REDDIT_LINK,
    Subreddit,
    TimePeriod,
    TimePeriodInterval,
    get_reddit_posts_json,
    load_config_from_dict,
)
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import (
    reply_text_with_chunks,
    send_text_with_chunks,
)

LLM_SYSTEM_PROMPT = (
    "You are an assistant that summarizes reddit posts. "
    "Summarize the following text in one sentence. "
    # "Provide the summary directly, without introductory phrases or extra words. "
    # "Focus on being concise and on the point."
)

DEFAULT_SUB = "python"


async def generate_reddit_posts_summary(
    subreddit: str, time_period: str, limit: int
) -> str:
    posts = get_reddit_posts_json(subreddit, time_period=time_period, limit=limit)
    if posts:
        response = (
            f"*Top {limit} {time_period} posts from "
            f"[r/{subreddit}]({REDDIT_LINK}/r/{subreddit}/top/?t={time_period}):*\n\n"
        )

        for post in posts:
            if post.selftext:
                post_summary = escape_markdown(
                    await summarize(post.selftext, LLM_SYSTEM_PROMPT), version=2
                )
            else:
                post_summary = "Post just contains an image or a link\\."

            post_title = escape_markdown(post.title, version=2)
            post_link = escape_markdown(post.link, version=2)
            response += (
                f"*[{post.score} \\| {post_title}]({post_link})*\n{post_summary}\n\n"
            )
        return response
    return "Failed to fetch posts. Please try again later."


async def get_reddit_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    subreddit = args[0] if args else DEFAULT_SUB
    time_period = args[1] if args and len(args) > 1 else TimePeriod.MONTH
    limit = int(args[2]) if args and len(args) > 2 else 10
    response = await generate_reddit_posts_summary(subreddit, time_period, limit)
    await reply_text_with_chunks(
        update, response, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )


async def send_reddit_posts(
    subreddit: Subreddit, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = await generate_reddit_posts_summary(
        subreddit.name, subreddit.period, subreddit.limit
    )
    await send_text_with_chunks(
        context, message, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )


async def process_subreddits(context: ContextTypes.DEFAULT_TYPE) -> None:
    database.connect()
    subreddits_config = load_config_from_dict(REDDIT_SUBREDDITS)
    database.create_subreddits_table(asdict(subreddits_config)["subreddits"])

    now = datetime.now()
    for subreddit_data in database.get_all_subreddits():
        subreddit_data.pop("_id")
        subreddit = Subreddit(**subreddit_data)

        if (
            not subreddit.timestamp
            or (
                subreddit.period == TimePeriod.MONTH
                and now - subreddit.timestamp
                >= timedelta(seconds=TimePeriodInterval.MONTH)
            )
            or (
                subreddit.period == TimePeriod.YEAR
                and now - subreddit.timestamp
                >= timedelta(seconds=TimePeriodInterval.YEAR)
            )
        ):

            logger.info(now - subreddit.timestamp)
            await send_reddit_posts(subreddit, context)
            subreddit.timestamp = now
            database.update_subreddit(asdict(subreddit))
            database.disconnect()
            return


application.add_handler(
    CommandHandler(
        BotCommands.GET, get_reddit_posts, filters=filters.User(TELEGRAM_CHAT_ID)
    )
)

application.job_queue.run_repeating(
    process_subreddits, interval=TimePeriodInterval.DAY, first=10
)

# schedule_jobs(application.job_queue)


# # print(application.job_queue.jobs())
