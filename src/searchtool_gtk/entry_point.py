import sys
import warnings

from .config import build_modes_from_config_file
from .exceptions import SearchToolValidationError
from .gui import SearchToolApp


def entry_point() -> None:
    warnings.simplefilter('always')

    try:
        config_items = build_modes_from_config_file()
    except SearchToolValidationError as err:
        if err.__cause__:
            raise SystemExit(f'Error: {err}. {err.__cause__}.') from err

        raise SystemExit(f'Error: {err}.') from err

    app = SearchToolApp(config_items)
    app.run(sys.argv)
