import copy
import logging
import time
from datetime import datetime

from gevent import monkey

monkey.patch_all()

import json  # noqa: E402

import requests  # noqa: E402

from modules import utils  # noqa: E402
from modules.models import App, Cache, Result  # noqa: E402


class GOGAppFilter:
    # None = null (default release branch)
    def __init__(self, id, filter=None):
        self.id = id
        self.filter = filter

    def __str__(self):
        # GOG uses null for main branch
        # null != "null" so we add quotes around strings to avoid confusion
        return (
            self.id + ":" + ("null" if self.filter is None else '"' + self.filter + '"')
        )


class GOG:
    def __init__(self, app_ids, notifier, ignore_first):
        self.logger = logging.getLogger(__name__)
        self.timestamp = None

        utils.create_directory("./cache/gog")
        self.cache = Cache(
            "./cache/gog/latest_data.json",
            "./cache/gog/old_data.json",
            "./cache/gog/tmp_data.json",
            "./cache/gog/latest_result.json",
        )

        self.old_result = {}
        self.new_result = utils.load_json_as_dict(self.cache.result)

        self.ignore_first = ignore_first

        self.apps = []

        for _app_id in app_ids:
            _app = _app_id.split(":")
            new_filter = GOGAppFilter(id=_app[0])
            if len(_app) != 1:
                new_filter = GOGAppFilter(id=_app[0], filter=_app[1])
            self.apps.append(new_filter)

            # null != "null"
            _app_id = str(new_filter)
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

    def gather_app_info(self):
        self.logger.info(
            "Request product information for apps: {}".format([a.id for a in self.apps])
        )
        _product_info = {}
        for a in self.apps:
            if a.id not in _product_info:
                try:
                    # get game name
                    _response = requests.get(
                        "https://api.gog.com/products/" + str(a.id)
                    )
                    if _response.status_code != 200:
                        self.logger.error(
                            "GOG api request for "
                            + str(a.id)
                            + " returned status code "
                            + str(_response.status_code)
                            + " "
                            + _response.url
                        )
                        continue
                    _response.close()
                    _game_name = _response.json()["title"]

                    # get branch info
                    _response = requests.get(
                        "https://content-system.gog.com/products/"
                        + str(a.id)
                        + "/os/windows/builds?generation=2"
                    )
                    if _response.status_code != 200:
                        self.logger.error(
                            "GOG content-system request for "
                            + str(a.id)
                            + " returned status code "
                            + str(_response.status_code)
                            + " "
                            + _response.url
                        )
                        continue
                    _product_info[a.id] = _response.json()
                    _product_info[a.id]["name"] = _game_name
                except Exception as e:
                    self.logger.error(e, stack_info=True, exc_info=True)
                finally:
                    _response.close()

        self.logger.info("Cache raw data as {}".format(self.cache.tmp_data))
        utils.save_dict_as_json(_product_info, self.cache.tmp_data)

        self.old_result = copy.copy(self.new_result)

        _latest_info = {}

        for _product in _product_info:
            # GOG can contain multiple entries for each branch,
            # use the one with the latest timestamp
            for _release in _product_info[_product]["items"]:
                # null != "null" so we add quotes around strings to avoid confusion
                _branch_key = str(
                    GOGAppFilter(_release["product_id"], _release["branch"])
                )
                # extract timestamp
                _release["timestamp"] = time.mktime(
                    datetime.strptime(
                        _release["date_published"], "%Y-%m-%dT%H:%M:%S%z"
                    ).timetuple()
                )
                _release["name"] = _product_info[_product]["name"]
                if _branch_key not in _latest_info:
                    _latest_info[_branch_key] = {"timestamp": -1}
                if _latest_info[_branch_key]["timestamp"] < _release["timestamp"]:
                    _latest_info[_branch_key] = _release

        # we now have the latest timetamp  for each branch
        for _app in self.apps:
            self.logger.info(
                "Gather updated data from raw data for {} in branch: {}".format(
                    _app.id, json.dumps(_app.filter)
                )
            )

            _last_updated = None
            if self.old_result and str(_app) in self.old_result:
                _last_updated = self.old_result[str(_app)].last_updated
            key = str(_app)
            self.new_result[key] = Result(
                app=App(
                    id=key,
                    name=_latest_info[key]["name"],
                ),
                data=_latest_info[key]["timestamp"],
                last_checked=self.timestamp,
                last_updated=_last_updated,
            )

        return

    def is_updated(self):
        self.gather_app_info()

        _is_updated = False
        _updated_apps = []

        for _app in self.apps:
            key = str(_app)
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
