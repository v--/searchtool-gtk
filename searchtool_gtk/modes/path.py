from pathlib import Path

from gi.repository import Gtk, GLib

from ..mode import SearchToolMode


# This is an abstract base class for several real modes
class PathMode(SearchToolMode[Path, tuple[int, str]]):
    recent: Gtk.RecentManager

    def get_main_item_label(self, item: Path):
        return item.name

    def get_secondary_item_label(self, item: Path):
        return item.parent.as_posix()

    def get_item_sort_keys(self, item: Path):
        timestamp = 0
        uri = item.as_uri()

        if self.recent.has_item(uri):
            info = self.recent.lookup_item(uri)

            if info is not None:
                timestamp = info.get_modified().to_unix()

        return [timestamp, item.as_posix()]

    def match_item(self, item: Path, filter_string: str):
        return filter_string.casefold() in item.as_posix().casefold()

    def bump_item(self, item: Path):
        self.recent.add_item(item.as_uri())
