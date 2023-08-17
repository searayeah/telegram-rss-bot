import aiohttp
from bs4 import BeautifulSoup
from bot import RSS_LIMIT, FILTER
from urllib.parse import urlparse
import logging

# import requests
# def get_rss_feed(rss_link, channel_name, limit):
#
#     rss_feed = requests.get(rss_link).json()
#     return rss_feed

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def get_rss_feed(channel_name):
    rss_link = (
        f"https://rsshub.app/telegram/channel/{channel_name}.json?limit={RSS_LIMIT}"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(rss_link) as resp:
            rss_feed = await resp.json()
            logger.info(f"Loaded rss_feed from {channel_name}")
            return rss_feed


async def get_telegram_channel_posts(channel_name):
    rss_feed = await get_rss_feed(channel_name)
    id_to_post = {}
    for item in reversed(rss_feed["items"]):
        id_to_post[item["id"]] = item["content_html"]
    logger.info(f"{rss_feed['title']}: got {len(id_to_post)} posts")
    return rss_feed["title"], id_to_post


async def get_new_telegram_channel_posts(channel_name, id_to_post_old):
    title, id_to_post_current = await get_telegram_channel_posts(channel_name)
    id_to_post_new = {}
    for key in id_to_post_current:
        if key not in id_to_post_old:
            id_to_post_new[key] = id_to_post_current[key]
    logger.info(
        f"{title}: {len(id_to_post_old)} old posts, found {len(id_to_post_new)} new posts"
    )
    return title, id_to_post_new


def filter_content(id_to_post, allowed_words):
    id_to_post_filtered = {}
    for key in id_to_post:
        for word in allowed_words:
            if word in id_to_post[key]:
                id_to_post_filtered[key] = id_to_post[key]
    return id_to_post_filtered


async def get_new_filtered_telegram_channel_posts(
    channel_name, id_to_post_old, allowed_words
):
    title, id_to_post_new = await get_new_telegram_channel_posts(
        channel_name, id_to_post_old
    )
    if FILTER:
        id_to_post_new_filtered = filter_content(id_to_post_new, allowed_words)
    else:
        id_to_post_new_filtered = id_to_post_new
    logger.info(
        f"{title}: {len(id_to_post_new)} new posts, found {len(id_to_post_new_filtered)} filtered posts"
    )
    return title, id_to_post_new_filtered


def get_channel_name_from_url(telegram_channel_url):
    chars = "/"
    parsed_url = urlparse(telegram_channel_url)
    channel_name = parsed_url.path.strip(chars)
    return channel_name


def sanitize_html(value):
    telegram_html_valid_tags = [
        "strong",
        "b",
        "i",
        "em",
        "u",
        "ins",
        "s",
        "strike",
        "del",
        "a",
        "pre",
        "code",
        "tg-emoji",
    ]
    soup = BeautifulSoup(value, features="html.parser")

    images = []

    for tag in soup.find_all(True):
        if tag.name == "img":
            images.append(tag["src"])
        elif tag.name == "br":
            tag.replace_with("\n" + tag.text)
            continue

        if tag.name not in telegram_html_valid_tags:
            tag.unwrap()
    logger.info(f"Found {len(images)} images")
    return {"text": str(soup), "photo": images}
