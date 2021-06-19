import copy
import logging
import re
from datetime import datetime

import ms_cv
import requests

from modules import utils
from modules.models import App, Cache, Result


class MSStoreFilter:
    def __init__(self, id, filter="Windows.Desktop"):
        self.id = id
        self.filter = filter


class MSStore:
    def __init__(self, app_ids, notifier, ignore_first, market):
        self.logger = logging.getLogger(__name__)
        self.old_result = {}
        self.new_result = {}
        self.timestamp = None

        self.apps = []
        for _app_id in app_ids:
            _app = _app_id.split(":")
            if len(_app) == 1:
                self.apps.append(MSStoreFilter(id=_app[0]))
            else:
                self.apps.append(MSStoreFilter(id=_app[0], filter=_app[1]))
        self.notifier = notifier
        self.ignore_first = ignore_first

        utils.create_directory("./cache/msstore")
        self.cache = Cache(
            "./cache/msstore/latest_data.json",
            "./cache/msstore/old_data.json",
            "./cache/msstore/tmp_data.json",
            "./cache/msstore/latest_result.json",
        )
        self.market = market

    def gather_app_info(self):
        self.logger.info(
            "Request product information for apps: {}".format([a.id for a in self.apps])
        )

        _cv = ms_cv.CorrelationVector()
        _endpoint = "https://displaycatalog.mp.microsoft.com/v7.0/products"
        _headers = {"MS-CV": _cv.get_value()}
        _params = {
            "languages": "en_US",
            "market": self.market,
            "actionFilter": "Browse",
            "bigIds": ",".join([a.id for a in self.apps]),
        }

        _product_info = requests.get(
            url=_endpoint, headers=_headers, params=_params
        ).json()

        self.logger.info("Cache raw data as {}".format(self.cache.tmp_data))
        utils.save_dict_as_json(_product_info, self.cache.tmp_data)

        self.old_result = copy.copy(self.new_result)
        for _app in self.apps:
            self.logger.info(
                "Gather updated data from raw data for {} for: {}".format(
                    _app.id, _app.filter
                )
            )

            _current_product = {}
            for _product in _product_info["Products"]:
                if _product["ProductId"].lower() == _app.id.lower():
                    _current_product = _product
                    break

            _name = _current_product["DisplaySkuAvailabilities"][0]["Sku"][
                "LocalizedProperties"
            ][0]["SkuTitle"]

            _package_fullname = []

            for _package in _current_product["DisplaySkuAvailabilities"][0]["Sku"][
                "Properties"
            ]["Packages"]:
                if _package["PlatformDependencies"][0]["PlatformName"] == _app.filter:
                    _fullname = ""
                    if _package["PackageFullName"]:
                        _fullname = _package["PackageFullName"]
                    elif _package["PackageDownloadUris"]:
                        _fullname = re.sub(
                            "^.*/", "", _package["PackageDownloadUris"][0]["Uri"]
                        )
                    _package_fullname.append(_fullname)

            _package_fullname.sort()

            _last_updated = None
            if self.old_result and _app.id in self.old_result:
                _last_updated = self.old_result[_app.id].last_updated

            self.new_result[_app.id] = Result(
                app=App(
                    id=_app.id,
                    name=_name,
                ),
                data=",".join(_package_fullname),
                last_checked=self.timestamp,
                last_updated=_last_updated,
            )

        return

    def is_updated(self):
        self.gather_app_info()

        _is_updated = False
        _updated_apps = []

        print(self.old_result)
        for _app in self.apps:
            if (
                self.old_result is {}
                or _app.id not in self.old_result
                or self.old_result[_app.id].data != self.new_result[_app.id].data
            ):
                self.logger.info(
                    "Update detected for: {}".format(self.new_result[_app.id].app.name)
                )
                self.logger.info("New data: {}".format(self.new_result[_app.id].data))
                _is_updated = True
                _updated_apps.append(self.new_result[_app.id].app)

                self.new_result[_app.id].last_updated = self.timestamp
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
