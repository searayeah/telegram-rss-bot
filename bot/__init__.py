import logging
from os import environ

import yaml
from dotenv import load_dotenv
from telegram.ext import Application

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


load_dotenv(".env")

TELEGRAM_CHAT_ID = int(environ["TELEGRAM_CHAT_ID"])
TELEGRAM_TOKEN = environ["TELEGRAM_TOKEN"]


OLLAMA_HOST = "http://ollama.seara.com"
OLLAMA_MODEL = "llama3.2"

with open("bot/config/telegram_channels_filter.yaml") as f:
    FILTER_WORDS = yaml.safe_load(f)
    logger.info(f"Loaded FILTER_WORDS {FILTER_WORDS}")

with open("bot/config/telegram_channels_links.yaml") as f:
    CHANNEL_URLS = yaml.safe_load(f)
    logger.info(f"Loaded CHANNEL_URLS {CHANNEL_URLS}")

RSS_LIMIT = 50
UPDATE_TIME = 60 * 60 * 5.5
FILTER = True

with open("bot/config/reddit.yaml") as f:
    REDDIT_SUBREDDITS = yaml.safe_load(f)
    logger.info(f"Loaded subreddits {REDDIT_SUBREDDITS}")


application = Application.builder().token(TELEGRAM_TOKEN).build()
