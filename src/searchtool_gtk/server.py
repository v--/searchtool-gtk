import sys

from .config import load_modes_from_config_file
from .exceptions import SearchToolValidationError
from .gui import SearchToolApp


def server_cli() -> int:
    try:
        config_items = load_modes_from_config_file()
    except SearchToolValidationError as err:
        if err.__cause__:
            raise SystemExit(f'Error: {err}. {err.__cause__}.') from err

        raise SystemExit(f'Error: {err}.') from err

    app = SearchToolApp(config_items)
    return app.run(sys.argv)
