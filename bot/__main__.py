from telegram import Update

from bot import application
from bot.modules import reddit  # pylint: disable=unused-import # noqa: F401


def main():
    application.run_polling(allowed_updates=Update.ALL_TYPES)


main()
