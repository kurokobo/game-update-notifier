import logging
import os
import time
from datetime import datetime
from os.path import dirname, join

from dotenv import load_dotenv

from modules.steam import Steam
from modules.msstore import MSStore
from modules.epicgames import EpicGames
from modules.discord import Discord

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

log_format = "%(asctime)s %(filename)s:%(name)s:%(lineno)d [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
)
logger = logging.getLogger(__name__)


def main():

    IGNORE_FIRST_NOTIFICATION = os.getenv("IGNORE_FIRST_NOTIFICATION").lower() == "true"
    CHECK_INTERVAL_SEC = int(os.getenv("CHECK_INTERVAL_SEC"))

    WATCH_STEAM = os.getenv("WATCH_STEAM").lower() == "true"
    STEAM_APP_IDS = [
        x.strip()
        for x in os.getenv("STEAM_APP_IDS").strip('"').strip("'").split(",")
        if not os.getenv("STEAM_APP_IDS") == ""
    ]

    WATCH_MSSTORE = os.getenv("WATCH_MSSTORE").lower() == "true"
    MSSTORE_APP_IDS = [
        x.strip()
        for x in os.getenv("MSSTORE_APP_IDS").strip('"').strip("'").split(",")
        if not os.getenv("MSSTORE_APP_IDS") == ""
    ]
    MSSTORE_MARKET = os.getenv("MSSTORE_MARKET")

    WATCH_EPICGAMES = os.getenv("WATCH_EPICGAMES").lower() == "true"
    EPICGAMES_APP_IDS = [
        x.strip()
        for x in os.getenv("EPICGAMES_APP_IDS").strip('"').strip("'").split(",")
        if not os.getenv("EPICGAMES_APP_IDS") == ""
    ]

    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    DISCORD_MENTION_ROLE_IDS = [
        x.strip()
        for x in os.getenv("DISCORD_MENTION_ROLE_IDS").strip('"').strip("'").split(",")
        if not os.getenv("DISCORD_MENTION_ROLE_IDS") == ""
    ]
    DISCORD_MENTION_USER_IDS = [
        x.strip()
        for x in os.getenv("DISCORD_MENTION_USER_IDS").strip('"').strip("'").split(",")
        if not os.getenv("DISCORD_MENTION_USER_IDS") == ""
    ]

    current_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_path)

    if WATCH_STEAM:
        steam_notifier = Discord(
            webhook_url=DISCORD_WEBHOOK_URL,
            role_ids=DISCORD_MENTION_ROLE_IDS,
            user_ids=DISCORD_MENTION_USER_IDS,
            platform="Steam",
            thumb_url=(
                "https://github.com/kurokobo/game-update-notifier/raw/main/"
                "assets/steam.png"
            ),
            embed_color="1e90ff",
        )
        steam = Steam(STEAM_APP_IDS, steam_notifier, IGNORE_FIRST_NOTIFICATION)

    if WATCH_MSSTORE:
        msstore_notifier = Discord(
            webhook_url=DISCORD_WEBHOOK_URL,
            role_ids=DISCORD_MENTION_ROLE_IDS,
            user_ids=DISCORD_MENTION_USER_IDS,
            platform="Microsoft Store",
            thumb_url=(
                "https://github.com/kurokobo/game-update-notifier/raw/main/"
                "assets/msstore.png"
            ),
            embed_color="e6e6fa",
        )
        msstore = MSStore(
            MSSTORE_APP_IDS, msstore_notifier, IGNORE_FIRST_NOTIFICATION, MSSTORE_MARKET
        )

    if WATCH_EPICGAMES:
        epicgames_notifier = Discord(
            webhook_url=DISCORD_WEBHOOK_URL,
            role_ids=DISCORD_MENTION_ROLE_IDS,
            user_ids=DISCORD_MENTION_USER_IDS,
            platform="Epic Games",
            thumb_url=(
                "https://github.com/kurokobo/game-update-notifier/raw/main/"
                "assets/epicgames.png"
            ),
            embed_color="11cf59",
        )
        epicgames = EpicGames(
            EPICGAMES_APP_IDS, epicgames_notifier, IGNORE_FIRST_NOTIFICATION
        )

    while True:
        logger.info("Loop start: {}".format(datetime.now()))

        if WATCH_STEAM:
            steam.check_update()

        if WATCH_MSSTORE:
            msstore.check_update()

        if WATCH_EPICGAMES:
            epicgames.check_update()

        logger.info("Will sleep {} seconds".format(CHECK_INTERVAL_SEC))
        time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    main()
