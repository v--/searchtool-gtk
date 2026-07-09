import pathlib
from typing import override

from searchtool_gtk.access_journal import SearchToolAccessJournal

from .base import SearchToolCollator
from .string import StringCollator


class PathCollator(SearchToolCollator[pathlib.Path]):
    journal: SearchToolAccessJournal[pathlib.Path]
    str_collator: StringCollator

    def __init__(self, journal: SearchToolAccessJournal[pathlib.Path], str_collator: StringCollator | None = None) -> None:
        self.journal = journal
        self.str_collator = str_collator or StringCollator()

    @override
    def compare(self, a: pathlib.Path, b: pathlib.Path) -> int:
        at = self.journal.get_last_access(a)
        bt = self.journal.get_last_access(b)

        if at == bt:
            return self.str_collator.compare(str(a), str(b))

        if at is None:
            return 1

        if bt is None:
            return -1

        # We want show the smallest timestamp first
        return 1 if at < bt else -1

    @override
    def match_item(self, item: pathlib.Path, filter_string: str) -> bool:
        return self.str_collator.match_item(str(item), filter_string)
