import datetime
import json
import logging
import os

from steam.client import SteamClient
from steam.enums import EResult

logger = logging.getLogger(__name__)
client = SteamClient()


def save_dict_as_json(dict, path):
    with open(path, mode="wt", encoding="utf-8") as file:
        json.dump(dict, file, ensure_ascii=False, indent=2)


def get_updated_time(app_id, info_cache, branch):
    try:
        logger.info("Request product information for app_id: {}".format(app_id))
        product_info = client.get_product_info(apps=[app_id])

        logger.info("Save product information to {}".format(info_cache))
        save_dict_as_json(product_info, info_cache)

        logger.info("Obtain last updated time of branch: {}".format(branch))
        updated_time = int(
            product_info["apps"][app_id]["depots"]["branches"][branch]["timeupdated"]
        )

        logger.info(
            "The last updated time is: {} ({})".format(
                datetime.datetime.utcfromtimestamp(updated_time), updated_time
            )
        )

        return {
            "app_name": product_info["apps"][app_id]["common"]["name"],
            "updated_time": updated_time,
        }
    except Exception as e:
        logger.info("Failed to gather information: {}".format(e))
        return None


def check_if_updated(current, time_cache, ignore_first):
    if os.path.exists(time_cache):
        logger.info("Read cached updated time")
        with open(time_cache) as file:
            latest = int(file.read())
    elif ignore_first:
        logger.info("No cache exists. To ignore first notification, fake cached time")
        latest = current
    else:
        logger.info("No cache exists. Will be compare to zero")
        latest = 0

    logger.info(
        "Cached updated time : {} ({})".format(
            datetime.datetime.utcfromtimestamp(int(latest)), latest
        )
    )
    logger.info(
        "Current updated time: {} ({})".format(
            datetime.datetime.utcfromtimestamp(int(current)), current
        )
    )

    logger.info("Save current updated time to cache file: {}".format(time_cache))
    with open(time_cache, mode="w") as file:
        file.write(str(current))

    if int(current) > latest:
        logger.info("Updated")
        return True
    else:
        logger.info("Not updated")
        return False


def Login():
    logged_on = client.logged_on
    logger.info("Is logged on: {}".format(logged_on))

    if logged_on:
        logger.info("Already logged in")
        return True

    logger.info("Try log in to Steam")
    if client.relogin_available:
        logger.info("Invoke relogin")
        login = client.relogin()
    else:
        logger.info("Invoke anonymous login")
        login = client.anonymous_login()
    logger.info("Result: {}".format(login))

    logged_on = client.logged_on
    logger.info("Is logged on: {}".format(logged_on))

    if login == EResult.OK or client.logged_on:
        logger.info("Successful logged in")
        return True
    else:
        logger.error("Failed to log in to Steam")
        return False


def Watch(app_id, info_cache, time_cache, branch, ignore_first):
    logger.info("Check the last updated time of app_id: {}".format(app_id))
    updated_time = get_updated_time(
        app_id,
        info_cache,
        branch,
    )
    if updated_time is None:
        logger.error("Failed to obtain last updated time from Steam")
        return None

    logger.info("Check if the product is updated ")
    is_updated = check_if_updated(
        updated_time["updated_time"], time_cache, ignore_first
    )
    return {
        "timestamp": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "app_id": app_id,
        "app_name": updated_time["app_name"],
        "updated": is_updated,
        "branch": branch,
        "timeupdated": {
            "epoc": updated_time["updated_time"],
            "str": datetime.datetime.utcfromtimestamp(
                updated_time["updated_time"]
            ).strftime("%Y/%m/%d %H:%M:%S"),
        },
    }


def Logout():
    logger.info("Invoke logged out")
    client.logout()
