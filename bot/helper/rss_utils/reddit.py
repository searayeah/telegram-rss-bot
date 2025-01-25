from dataclasses import dataclass

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
    period: TimePeriod
    limit: int


@dataclass
class SubredditsConfig:
    subreddits: list[Subreddit]


class TimePeriodInterval:
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    MONTH = 2592000
    YEAR = 31536000


time_period_to_interval = {
    TimePeriod.HOUR: TimePeriodInterval.HOUR,
    TimePeriod.DAY: TimePeriodInterval.DAY,
    TimePeriod.WEEK: TimePeriodInterval.WEEK,
    TimePeriod.MONTH: TimePeriodInterval.MONTH,
    TimePeriod.YEAR: TimePeriodInterval.YEAR,
}


def load_config_from_yaml(yaml_config: dict) -> SubredditsConfig:
    print(yaml_config)
    subreddits = [
        Subreddit(
            name=sub["name"],
            period=sub["period"],
            limit=sub["limit"],
        )
        for sub in yaml_config["subreddits"]
    ]
    return SubredditsConfig(subreddits=subreddits)
