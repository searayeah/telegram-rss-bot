from dataclasses import dataclass, field
from datetime import datetime, timedelta

import requests
from loguru import logger

REDDIT_LINK = "https://www.reddit.com"
HTTP_OK = 200


class TimePeriod:
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"


@dataclass
class RedditPost:
    title: str
    link: str
    author: str
    score: int
    num_comments: int
    created_utc: float
    subreddit: str
    selftext: str
    link_flair_text: str


@dataclass
class Subreddit:
    name: str
    period: str
    limit: int
    exclude_flairs: list[str] = field(default_factory=list)
    include_flairs: list[str] = field(default_factory=list)
    timestamp: datetime = None


@dataclass
class SubredditsConfig:
    subreddits: list[Subreddit]


class TimePeriodInterval:
    HOUR = timedelta(hours=1)
    DAY = timedelta(days=1)
    WEEK = timedelta(weeks=1)
    MONTH = timedelta(days=30)
    YEAR = timedelta(days=365)


time_period_to_interval = {
    TimePeriod.HOUR: TimePeriodInterval.HOUR,
    TimePeriod.DAY: TimePeriodInterval.DAY,
    TimePeriod.WEEK: TimePeriodInterval.WEEK,
    TimePeriod.MONTH: TimePeriodInterval.MONTH,
    TimePeriod.YEAR: TimePeriodInterval.YEAR,
}

SYMBOL_TO_URL_SYMBOL = {"(": "%28", ")": "%29", " ": "+", ":": "%3A"}

EXCLUDE_FLAIR_WORD = "-flair:"
INCDULE_FLAIR = "flair:"
LOGICAL_AND = " AND "


def generate_flair_query(
    exclude_flairs: list[str] | None = None, include_flairs: list[str] | None = None
) -> str:

    def generate(flair_word: str, flairs: list[str]) -> str:
        query = ""
        query += flair_word
        query += flairs[0]

        for flair in flairs[1:]:
            query += LOGICAL_AND
            query += flair_word
            query += flair
        for symbol, code in SYMBOL_TO_URL_SYMBOL.items():
            query = query.replace(symbol, code)
        return query

    if exclude_flairs:
        return generate(EXCLUDE_FLAIR_WORD, exclude_flairs)
    if include_flairs:
        return generate(INCDULE_FLAIR, include_flairs)
    return ""


def load_config_from_dict(yaml_config: dict) -> SubredditsConfig:
    subreddits = [
        Subreddit(
            name=sub["name"],
            period=sub["period"],
            limit=sub["limit"],
            exclude_flairs=sub.get("exclude_flairs", []),
            include_flairs=sub.get("include_flairs", []),
        )
        for sub in yaml_config["subreddits"]
    ]
    return SubredditsConfig(subreddits=subreddits)


def get_reddit_posts_json(
    subreddit: str,
    time_period: str = "month",
    limit: int = 100,
    exclude_flairs: list[str] | None = None,
    include_flairs: list[str] | None = None,
) -> list[RedditPost]:

    subreddit_link = f"{REDDIT_LINK}/r/{subreddit}"
    if exclude_flairs or include_flairs:
        flair_query = generate_flair_query(exclude_flairs, include_flairs)
        url = f"{subreddit_link}/search.json?q={flair_query}&sort=top&t={time_period}&limit={limit}&restrict_sr=on"  # noqa: E501
    else:
        url = f"{subreddit_link}/top.json?t={time_period}&limit={limit}"

    logger.info(f"Fetching data from {url}")

    headers = {"User-Agent": "RedditBot/1.0"}  # Custom User-Agent to prevent blocks
    response = requests.get(url, headers=headers, timeout=10)

    if response.status_code != HTTP_OK:
        error_message = f"Failed to fetch data from {url}: HTTP {response.status_code}"
        raise ValueError(error_message)

    data = response.json()
    posts = []

    for post in data["data"]["children"]:
        post_data = post["data"]
        posts.append(
            RedditPost(
                title=post_data["title"],
                link=f"{REDDIT_LINK}{post_data['permalink']}",
                author=post_data["author"],
                score=post_data["score"],
                num_comments=post_data["num_comments"],
                created_utc=post_data["created_utc"],
                subreddit=post_data["subreddit"],
                selftext=post_data["selftext"],
                link_flair_text=post_data["link_flair_text"],
            )
        )

    return posts
