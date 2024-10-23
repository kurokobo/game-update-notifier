import copy
import logging
from datetime import datetime

from steam.client import SteamClient
from steam.enums import EResult

from modules import utils  # noqa: E402
from modules.models import App, Cache, Result  # noqa: E402


class SteamAppFilter:
    def __init__(self, id, filter="public"):
        self.id = id
        self.filter = filter


class Steam:
    def __init__(self, app_ids, notifier, ignore_first):
        self.logger = logging.getLogger(__name__)
        self.client = SteamClient()
        self.timestamp = None

        utils.create_directory("./cache/steam")
        self.cache = Cache(
            "./cache/steam/latest_data.json",
            "./cache/steam/old_data.json",
            "./cache/steam/tmp_data.json",
            "./cache/steam/latest_result.json",
        )

        self.old_result = {}
        self.new_result = utils.load_json_as_dict(self.cache.result)

        self.ignore_first = ignore_first

        self.apps = []

        for _app_id in app_ids:
            _app = _app_id.split(":")
            new_filter = SteamAppFilter(id=_app[0])
            if len(_app) != 1:
                new_filter = SteamAppFilter(id=_app[0], filter=_app[1])
            self.apps.append(new_filter)

            _app_id = new_filter.id + ":" + new_filter.filter
            if _app_id in self.new_result:
                # de-JSON
                self.new_result[_app_id] = Result(
                    app=App(
                        id=_app_id,
                        name=self.new_result[_app_id]["app"]["name"],
                    ),
                    data=self.new_result[_app_id]["data"],
                    last_checked=self.new_result[_app_id]["last_checked"],
                    last_updated=self.new_result[_app_id]["last_updated"],
                )

                # disable ignore_first because we're loading from a cached state
                self.ignore_first = False
        self.old_result = copy.copy(self.new_result)
        self.notifier = notifier

    def login(self):
        self.logger.info("Log in to Steam")

        if self.client.logged_on:
            self.logger.info("Already logged in")
            return True

        if self.client.relogin_available:
            self.logger.info("Invoke relogin")
            login = self.client.relogin()
        else:
            self.logger.info("Invoke anonymous login")
            login = self.client.anonymous_login()

        if login == EResult.OK:
            self.logger.info("Successful logged in")
            return True
        else:
            self.logger.error("Failed to log in to Steam")
            return False

    def gather_app_info(self):
        self.logger.info(
            "Request product information for apps: {}".format([a.id for a in self.apps])
        )
        _product_info = self.client.get_product_info(
            apps=[int(a.id) for a in self.apps]
        )

        self.logger.info("Cache raw data as {}".format(self.cache.tmp_data))
        utils.save_dict_as_json(_product_info, self.cache.tmp_data)

        self.old_result = copy.copy(self.new_result)
        for _app in self.apps:
            key = _app.id + ":" + _app.filter
            self.logger.info(
                "Gather updated data from raw data for {} in branch: {}".format(
                    _app.id, _app.filter
                )
            )

            _last_updated = None
            if self.old_result and key in self.old_result:
                _last_updated = self.old_result[key].last_updated
            key = _app.id + ":" + _app.filter
            self.new_result[key] = Result(
                app=App(
                    id=key,
                    name=_product_info["apps"][int(_app.id)]["common"]["name"],
                ),
                data=_product_info["apps"][int(_app.id)]["depots"]["branches"][
                    _app.filter
                ]["timeupdated"],
                last_checked=self.timestamp,
                last_updated=_last_updated,
            )

        return

    def is_updated(self):
        self.gather_app_info()

        _is_updated = False
        _updated_apps = []

        for _app in self.apps:
            key = _app.id + ":" + _app.filter
            if (
                self.old_result is {}
                or key not in self.old_result
                or self.old_result[key].data != self.new_result[key].data
            ):
                self.logger.info(
                    "Update detected for: {} ({})".format(
                        self.new_result[key].app.name, _app.filter
                    )
                )

                self.logger.info("New data: {}".format(self.new_result[key].data))
                _is_updated = True
                _updated_apps.append(self.new_result[key].app)

                self.new_result[key].last_updated = self.timestamp
                utils.replace_file(self.cache.latest_data, self.cache.old_data)

        self.logger.info("Cache filtered data as {}".format(self.cache.result))
        utils.save_dict_as_json(self.new_result, self.cache.result)
        utils.replace_file(self.cache.tmp_data, self.cache.latest_data)

        return _is_updated, _updated_apps

    def check_update(self):
        try:
            self.timestamp = datetime.now()

            if not self.login():
                self.logger.error("Failed to log in to Steam")
                return

            _is_updated, updated_apps = self.is_updated()

            if _is_updated:
                if self.ignore_first:
                    self.logger.info(
                        "Update detected, will skip notifying on the first time"
                    )
                    self.ignore_first = False
                else:
                    self.logger.info("Update detected, will fire notifying")
                    self.notifier.fire(updated_apps, self.timestamp)
            else:
                self.logger.info("No update detected.")

            return
        except Exception as e:
            self.logger.error(e, stack_info=True, exc_info=True)
            return
        finally:
            self.logout()

    def logout(self):
        self.logger.info("Log out from Steam")
        self.client.logout()
