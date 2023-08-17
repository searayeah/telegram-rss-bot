from telegram import Update
from bot import application
from bot.modules import telegram_channels_rss


def main():
    application.run_polling(allowed_updates=Update.ALL_TYPES)


main()
