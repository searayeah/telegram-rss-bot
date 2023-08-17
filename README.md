# telegram-rss-bot

This is a Telegram bot for parsing __Telegram channels__ feeds through RSS.

## Running

### Python

- Python 3.10+ is required

- Installing dependencies:

    ```shell
    pip install -r requirements
    ```

- Setting environment variables. Use `.env` file and `load_dotenv` in `bot/__init__.py` or export:

    ```shell
    export TELEGRAM_TOKEN="YOUR_TELEGRAM_TOKEN"
    export TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"
    ```

- Running:

    ```shell
    python -m bot
    ```

### Docker image

```shell
sudo docker run -e TELEGRAM_TOKEN="YOUR_TELEGRAM_TOKEN" -e TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID" searayeah/telegram-rss-bot:latest
```

## Config

Channels should be put in `bot/config/telegram_channels_links.yaml` config file as a list in `https://t.me/{channel_name}` or `{channel_name}` format.

There is also `RSS_LIMIT` global variable in `bot/__init__.py` that controls the number of channel posts to be parsed. I noticed that in Telegram the number is capped to 15-20.

> This number is limited by the length of Telegram channel preview.

To filter posts that bot sends you, you can set `FILTER = True` in `bot/__init__.py` and add key words to `bot/config/telegram_channels_filter.yaml` config file. Only posts that include key words will be sent to user.

## RSS provider and Limitations

Telegram has no RSS feed by default, so [RSSHub](https://rsshub.app/) is used to generate one per each channel. Due to being publicly hosted, RSSHub can only refresh feed every 5 hours. If requested earlier, it will just send cached version of previously sent channel posts.

The feed for each channel requested as a `.json` file, that must contain two keys: string `title` and list of `items`. Each `item` in a list is a Telegram channel post containing unique `id` (post link) and `content_html` (post content in html format).

To update channel posts more than once per 5 hour, one needs to use some other RSS feed generators or host it themself. To change RSS provider the `rss_link` should be reconfigured in `get_rss_feed` function in `bot/helper/telegram_channels_rss_parser.py`.

After that (if the RSS service cache time is different) you can alter the refresh time by changing time in `UPDATE_TIME` variable in `bot/__init__.py`.

## TO-DO

- [ ] Add photos support
- [ ] Add other sources support
