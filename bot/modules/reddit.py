from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, JobQueue, filters
from telegram.helpers import escape_markdown

from bot import REDDIT_SUBREDDITS, TELEGRAM_CHAT_ID, application
from bot.helper.ext_utils.ollama import summarize
from bot.helper.reddit_rss_parser import REDDIT_LINK, get_reddit_posts_json
from bot.helper.rss_utils.reddit import (
    TimePeriod,
    load_config_from_yaml,
    time_period_to_interval,
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


async def generate_reddit_posts_summary(
    subreddit: str, time_period: str, limit: int
) -> str:
    posts = get_reddit_posts_json(subreddit, time_period=time_period, limit=limit)
    if posts:
        response = (
            f"*Top {time_period} posts from "
            f"[r/{subreddit}]({REDDIT_LINK}/r/{subreddit}/top/?t={time_period}):*\n\n"
        )

        for post in posts:
            print(post)
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
    subreddit = args[0] if args else "python"
    time_period = args[1] if args and len(args) > 1 else TimePeriod.MONTH
    limit = int(args[2]) if args and len(args) > 2 else 10
    response = await generate_reddit_posts_summary(subreddit, time_period, limit)
    await reply_text_with_chunks(
        update, response, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )


async def send_reddit_posts(context: ContextTypes.DEFAULT_TYPE) -> None:
    subreddit = context.job.data["subreddit"]
    message = await generate_reddit_posts_summary(
        subreddit.name, subreddit.period, subreddit.limit
    )
    await send_text_with_chunks(
        context, message, parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True
    )


def schedule_jobs(job_queue: JobQueue) -> None:
    subreddits_config = load_config_from_yaml(REDDIT_SUBREDDITS)

    for subreddit in subreddits_config.subreddits:
        job_queue.run_repeating(
            send_reddit_posts,
            interval=time_period_to_interval[subreddit.period],
            first=5,
            data={"subreddit": subreddit},
            name=f"fetch_{subreddit.name}_{subreddit.period}",
            chat_id=TELEGRAM_CHAT_ID,
        )


application.add_handler(
    CommandHandler(
        BotCommands.GET, get_reddit_posts, filters=filters.User(TELEGRAM_CHAT_ID)
    )
)

schedule_jobs(application.job_queue)
