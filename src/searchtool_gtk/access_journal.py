# ruff: file-ignore[import-outside-top-level]

import contextlib
import pathlib
from collections.abc import Hashable
from datetime import datetime
from typing import TYPE_CHECKING

from gi.repository import Gio, GLib

from searchtool_gtk.exceptions import SearchToolIntegrityError


if TYPE_CHECKING:
    from gi.repository import Gtk


def get_path_uri(path: pathlib.Path) -> str:
    """Encode a path as a GIO URI.

    The result differs from path.as_uri() on non-ascii paths.
    """
    gio_file = Gio.File.new_for_path(path.as_posix())
    return gio_file.get_uri()


class SearchToolAccessJournal[SearchToolItem: Hashable]:
    """An access journal backed by GTK.

    Only file system paths are supported, but it is easy to make it configurable.

    We load GTK lazily since it requires some initialization in the GUI code.
    """

    recent: 'Gtk.RecentManager'

    def __init__(self) -> None:
        from gi.repository import Gtk
        self.recent = Gtk.RecentManager()

    def get_last_access(self, item: SearchToolItem) -> datetime | None:
        if not isinstance(item, pathlib.Path):
            raise SearchToolIntegrityError('The GTK recent manager only supports files')

        with contextlib.suppress(GLib.GError):
            if info := self.recent.lookup_item(get_path_uri(item)):
                return datetime.fromtimestamp(info.get_modified().to_unix())

        return None

    def log_access(self, item: SearchToolItem) -> None:
        if not isinstance(item, pathlib.Path):
            raise SearchToolIntegrityError('The GTK recent manager only supports files')

        self.recent.add_item(get_path_uri(item))
