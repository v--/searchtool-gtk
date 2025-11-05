from dataclasses import dataclass
from typing import override

from .base import SearchToolCollator
from .string import StringCollator


@dataclass
class ClipHistItem:
    id: int
    value: str


class ClipHistCollator(SearchToolCollator[ClipHistItem]):
    str_collator: StringCollator

    def __init__(self, str_collator: StringCollator | None = None) -> None:
        self.str_collator = str_collator or StringCollator()

    @override
    def compare(self, a: ClipHistItem, b: ClipHistItem) -> int:
        if a.id == b.id:
            return 0

        # We want show the largest id (indicating the latest copy) first
        return 1 if a.id < b.id else -1

    @override
    def match_item(self, item: ClipHistItem, filter_string: str) -> bool:
        return self.str_collator.match_item(str(item.value), filter_string)
