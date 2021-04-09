import logging
import os
import time
from os.path import dirname, join

from dotenv import load_dotenv
from gevent import monkey

monkey.patch_all()

from modules import notifier, witness  # noqa: E402

# dotenv
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Load environment variables
APP_ID = int(os.getenv("APP_ID"))
WATCHED_BRANCH = os.getenv("WATCHED_BRANCH")

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

IGNORE_FIRST_NOTIFICATION = os.getenv("IGNORE_FIRST_NOTIFICATION").lower() == "true"
CHECK_INTERVAL_SEC = int(os.getenv("CHECK_INTERVAL_SEC"))
PRODUCT_INFO_CACHE = "./cache/product_info.json"
UPDATED_TIME_CACHE = "./cache/updated_time.txt"

# Logger
log_format = "%(asctime)s %(filename)s:%(name)s:%(lineno)d [%(levelname)s] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
)
logger = logging.getLogger(__name__)


def one_shot():
    logger.info("Log in to Steam")
    is_logged_in = witness.Login()
    if not is_logged_in:
        logger.error("Failed to log in to Steam")
        return False

    logger.info("Check if updated")
    is_updated = witness.Watch(
        APP_ID,
        PRODUCT_INFO_CACHE,
        UPDATED_TIME_CACHE,
        WATCHED_BRANCH,
        IGNORE_FIRST_NOTIFICATION,
    )
    logger.info("Result: {}".format(is_updated))

    if is_updated is not None and is_updated["updated"]:
        logger.info("Fire notification")
        notifier.Fire(
            DISCORD_WEBHOOK_URL,
            DISCORD_USER_ID,
            is_updated["app_name"],
            is_updated["app_id"],
            is_updated["branch"],
            is_updated["timeupdated"]["str"],
        )
    return True


def main():
    try:
        while True:
            logger.info("Loop start")
            result = one_shot()
            if result:
                logger.info(
                    "Loop successfully completed. Will sleep {} seconds".format(
                        CHECK_INTERVAL_SEC
                    )
                )
            else:
                logger.info(
                    "Loop failed. Will sleep {} seconds and retry".format(
                        CHECK_INTERVAL_SEC
                    )
                )
            time.sleep(CHECK_INTERVAL_SEC)
    except Exception as e:
        logger.error(e)
    finally:
        witness.Logout()


if __name__ == "__main__":
    main()
