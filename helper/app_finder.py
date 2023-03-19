import argparse

from gevent import monkey

monkey.patch_all()

import ms_cv  # noqa: E402
import requests  # noqa: E402
from legendary.cli import LegendaryCLI  # noqa: E402
from steam.client import SteamClient  # noqa: E402
from tabulate import tabulate  # noqa: E402


def gather_steam(id):
    _id = int(id)
    _client = SteamClient()

    try:
        _client.anonymous_login()
        _product_info = _client.get_product_info([_id])
    finally:
        _client.logout()

    _header = ["KEY", "App Id", "Name", "Branch", "Updated Time"]
    _table = []
    for _branch in _product_info["apps"][_id]["depots"]["branches"]:
        _name = _product_info["apps"][_id]["common"]["name"]
        _updated_time = -1
        if "timeupdated" in _product_info["apps"][_id]["depots"]["branches"][_branch]:
            _updated_time = _product_info["apps"][_id]["depots"]["branches"][_branch]["timeupdated"]
        _row = [
            "{}:{}".format(_id, _branch),
            _id,
            _name,
            _branch,
            _updated_time,
        ]
        _table.append(_row)

    print(tabulate(_table, _header))


def gather_msstore(id, market):
    _cv = ms_cv.CorrelationVector()
    _endpoint = "https://displaycatalog.mp.microsoft.com/v7.0/products"
    _headers = {"MS-CV": _cv.get_value()}
    _params = {
        "languages": "en_US",
        "market": market,
        "actionFilter": "Browse",
        "bigIds": id,
    }
    _product_info = requests.get(url=_endpoint, headers=_headers, params=_params).json()

    _header = ["KEY", "App Id", "Market", "Name", "Platform", "Package Id"]
    _table = []
    for _package in _product_info["Products"][0]["DisplaySkuAvailabilities"][0]["Sku"][
        "Properties"
    ]["Packages"]:
        _name = _product_info["Products"][0]["DisplaySkuAvailabilities"][0]["Sku"][
            "LocalizedProperties"
        ][0]["SkuTitle"]
        _platform_dependencies = _package["PlatformDependencies"][0]["PlatformName"]
        _package_id = _package["PackageId"]
        _row = [
            "{}:{}".format(id, _platform_dependencies),
            id,
            market,
            _name,
            _platform_dependencies,
            _package_id,
        ]
        _table.append(_row)

    print(tabulate(_table, _header))


def gather_epicgames():
    _client = LegendaryCLI(api_timeout=10.0)
    _client.core.login()
    _product_infos, _ = _client.core.get_game_and_dlc_list()

    _header = ["KEY", "App Id", "Name", "Build Version"]
    _table = []
    for _product_info in _product_infos:
        _data = vars(_product_info)
        _id = _data["app_name"]
        _name = _data["app_title"]
        _version = _data["asset_infos"]["Windows"]["build_version"]

        _row = [_id, _id, _name, _version]
        _table.append(_row)

    print(tabulate(_table, _header))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--platform",
        type=str,
        choices=["steam", "epicgames", "msstore"],
        help=(
            "specify the name of the platform that you want to gather. "
            "choices: steam, epicgames, msstore"
        ),
    )
    parser.add_argument(
        "-m",
        "--market",
        default="US",
        type=str,
        help="specify the market id for msstore. defaults to 'US'",
    )
    parser.add_argument(
        "-i",
        "--id",
        type=str,
        help="specify the id of the game. required for steam or msstore",
    )
    args = parser.parse_args()

    if args.platform == "steam":
        gather_steam(args.id)

    if args.platform == "msstore":
        gather_msstore(args.id, args.market)

    if args.platform == "epicgames":
        gather_epicgames()


if __name__ == "__main__":
    main()
