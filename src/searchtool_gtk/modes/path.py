import pathlib
from typing import override

from searchtool_gtk.access_journal import SearchToolAccessJournal
from searchtool_gtk.collation import PathCollator

from .base import SearchToolMode


# This is an abstract base class for several real modes
class PathMode(SearchToolMode[pathlib.Path]):
    journal: SearchToolAccessJournal[pathlib.Path]

    def __init__(self) -> None:
        self.journal = SearchToolAccessJournal()

    @override
    def get_collator(self) -> PathCollator:
        return PathCollator(self.journal)

    @override
    def get_main_item_label(self, item: pathlib.Path) -> str:
        return item.name

    @override
    def get_secondary_item_label(self, item: pathlib.Path) -> str:
        return item.parent.as_posix()

    @override
    def handle_selection_cancellation(self) -> None:
        pass
