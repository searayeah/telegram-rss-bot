from telegram.ext import Application
from dotenv import load_dotenv
from os import environ
import logging
import yaml


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


load_dotenv("../.env/telegram-rss-bot.env")

TELEGRAM_CHAT_ID = int(environ["TELEGRAM_CHAT_ID"])
TELEGRAM_TOKEN = environ["TELEGRAM_TOKEN"]

with open("bot/config/telegram_channels_filter.yaml", "r") as f:
    FILTER_WORDS = yaml.safe_load(f)
    logger.info(f"Loaded FILTER_WORDS {FILTER_WORDS}")

with open("bot/config/telegram_channels_links.yaml", "r") as f:
    CHANNEL_URLS = yaml.safe_load(f)
    logger.info(f"Loaded CHANNEL_URLS {CHANNEL_URLS}")

RSS_LIMIT = 50

UPDATE_TIME = 60 * 60 * 5.5

FILTER = True

application = Application.builder().token(TELEGRAM_TOKEN).build()
