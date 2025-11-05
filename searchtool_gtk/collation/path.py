import pathlib
from typing import override

from gi.repository import Gio, Gtk

from .base import SearchToolCollator
from .string import StringCollator


class PathCollator(SearchToolCollator[pathlib.Path]):
    recent: Gtk.RecentManager
    str_collator: StringCollator

    def __init__(self, recent: Gtk.RecentManager, str_collator: StringCollator | None = None) -> None:
        self.recent = recent
        self.str_collator = str_collator or StringCollator()

    def get_history_timestamp(self, item: pathlib.Path) -> int:
        gio_file = Gio.File.new_for_path(item.as_posix())
        uri = gio_file.get_uri()

        if self.recent.has_item(uri):
            info = self.recent.lookup_item(uri)

            if info is not None:
                return info.get_modified().to_unix()

        return 0

    @override
    def compare(self, a: pathlib.Path, b: pathlib.Path) -> int:
        at = self.get_history_timestamp(a)
        bt = self.get_history_timestamp(b)

        if at == bt:
            return self.str_collator.compare(str(a), str(b))

        # We want show the smallest timestamp first
        return 1 if at < bt else -1

    @override
    def match_item(self, item: pathlib.Path, filter_string: str) -> bool:
        return self.str_collator.match_item(str(item), filter_string)
