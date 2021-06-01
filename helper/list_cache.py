import json
import os
from tabulate import tabulate


def append_cache(table, platform, json_path):
    _json = {}
    if os.path.exists(json_path):
        with open(json_path) as file:
            _json = json.load(file)

    _table = table
    for _data in _json:
        _result = _json[_data]
        _row = [
            platform,
            _result["app"]["id"],
            _result["app"]["name"],
            _result["last_checked"],
            _result["last_updated"],
            _result["data"],
        ]
        _table.append(_row)

    return _table


def main():

    json_epicgames = "../cache/epicgames/latest_result.json"
    json_msstore = "../cache/msstore/latest_result.json"
    json_steam = "../cache/steam/latest_result.json"

    current_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_path)

    _header = ["Platform", "ID", "Name", "Last Checked", "Last Updated", "Data"]
    _table = []

    _table = append_cache(_table, "Epic Games", json_epicgames)
    _table = append_cache(_table, "Microsoft Store", json_msstore)
    _table = append_cache(_table, "Steam", json_steam)

    print(tabulate(_table, _header))


if __name__ == "__main__":
    main()
