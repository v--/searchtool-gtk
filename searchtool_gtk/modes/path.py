from pathlib import Path
from typing import Any, override

from gi.repository import Gtk

from ..collation import PathCollator
from .base import SearchToolMode


# This is an abstract base class for several real modes
class PathMode[ParamClass = Any](SearchToolMode[Path, ParamClass]):
    recent: Gtk.RecentManager

    @override
    def get_collator(self) -> PathCollator:
        return PathCollator(self.recent)

    @override
    def get_main_item_label(self, item: Path) -> str:
        return item.name

    @override
    def get_secondary_item_label(self, item: Path) -> str:
        return item.parent.as_posix()

    @override
    def bump_item(self, item: Path) -> None:
        self.recent.add_item(item.as_uri())

    @override
    def handle_selection_cancellation(self) -> None:
        pass
