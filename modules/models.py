from datetime import datetime


class Platform:
    def __init__(self, id, fullname):
        self.id = id
        self.fullname = fullname


class Cache:
    def __init__(self, latest_data, old_data, tmp_data, result):
        self.latest_data = latest_data
        self.old_data = old_data
        self.tmp_data = tmp_data
        self.result = result


class Result:
    def __init__(self, app, data, last_checked, last_updated=None):
        self.app = app
        self.data = data
        self.last_checked = last_checked
        self.last_updated = last_updated


class App:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class AppFilter:
    def __init__(self, app_id, filter):
        self.app_id = app_id
        self.filter = filter


def json_default(o):
    if isinstance(o, Result):
        if isinstance(o.last_updated, datetime):
            _last_updated = o.last_updated.isoformat()
        else:
            _last_updated = o.last_updated
        return {
            "app": {
                "id": o.app.id,
                "name": o.app.name,
            },
            "data": o.data,
            "last_checked": o.last_checked.isoformat(),
            "last_updated": _last_updated,
        }
    raise TypeError(repr(o) + " is not JSON serializable")
