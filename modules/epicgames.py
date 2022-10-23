import copy
import logging
from datetime import datetime

from legendary.cli import LegendaryCLI

from modules import utils
from modules.models import App, Cache, Result


class EpicGames:
    def __init__(self, app_ids, notifier, ignore_first):
        self.logger = logging.getLogger(__name__)
        self.client = LegendaryCLI(api_timeout=10.0)
        self.old_result = {}
        self.new_result = {}
        self.timestamp = None

        self.apps = app_ids
        self.notifier = notifier
        self.ignore_first = ignore_first

        utils.create_directory("./cache/epicgames")
        self.cache = Cache(
            "./cache/epicgames/latest_data.json",
            "./cache/epicgames/old_data.json",
            "./cache/epicgames/tmp_data.json",
            "./cache/epicgames/latest_result.json",
        )

    def gather_app_info(self):
        self.logger.info("Request product information for apps: {}".format(self.apps))
        _games, _ = self.client.core.get_game_and_dlc_list()

        _product_info = {"apps": {}}
        for _game in _games:
            _data = vars(_game)
            if _data["app_name"] in self.apps:
                _product_info["apps"][_data["app_name"]] = _data

        self.logger.info("Cache raw data as {}".format(self.cache.tmp_data))
        utils.save_dict_as_json(_product_info, self.cache.tmp_data)

        self.old_result = copy.copy(self.new_result)
        for _app in self.apps:
            self.logger.info("Gather updated data from raw data for: {}".format(_app))

            _last_updated = None
            if self.old_result and _app in self.old_result:
                _last_updated = self.old_result[_app].last_updated

            self.new_result[_app] = Result(
                app=App(
                    id=_app,
                    name=_product_info["apps"][_app]["app_title"],
                ),
                data=_product_info["apps"][_app]["asset_info"]["build_version"],
                last_checked=self.timestamp,
                last_updated=_last_updated,
            )

        return

    def is_updated(self):
        self.gather_app_info()

        _is_updated = False
        _updated_apps = []

        for _app in self.apps:
            if (
                self.old_result is {}
                or _app not in self.old_result
                or self.old_result[_app].data != self.new_result[_app].data
            ):
                self.logger.info(
                    "Update detected for: {}".format(self.new_result[_app].app.name)
                )
                self.logger.info("New data: {}".format(self.new_result[_app].data))
                _is_updated = True
                _updated_apps.append(self.new_result[_app].app)

                self.new_result[_app].last_updated = self.timestamp
                utils.replace_file(self.cache.latest_data, self.cache.old_data)

        self.logger.info("Cache filtered data as {}".format(self.cache.result))
        utils.save_dict_as_json(self.new_result, self.cache.result)
        utils.replace_file(self.cache.tmp_data, self.cache.latest_data)

        return _is_updated, _updated_apps

    def check_update(self):
        try:
            self.timestamp = datetime.now()

            if not self.client.core.login():
                self.logger.error("Failed to log in to Epig Games")
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
