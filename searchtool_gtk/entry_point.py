import sys

import xdg.BaseDirectory

from .config import build_modes_from_file
from .exceptions import SearchToolValidationError
from .gui import SearchToolApp


def entry_point() -> None:
    try:
        config_items = build_modes_from_file(
            xdg.BaseDirectory.load_first_config('searchtool.json')
        )
    except SearchToolValidationError as err:
        raise SystemExit(err)

    app = SearchToolApp(config_items)
    app.run(sys.argv)
