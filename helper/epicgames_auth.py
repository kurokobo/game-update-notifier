from legendary.cli import LegendaryCLI


def main():
    _client = LegendaryCLI(api_timeout=10.0)
    _args = {
        "import_egs_auth": None,
        "auth_code": None,
        "session_id": None,
        "ex_token": None,
        "auth_delete": None,
    }
    _args = type("dummy", (object,), _args)
    _client.auth(_args)


if __name__ == "__main__":
    main()
