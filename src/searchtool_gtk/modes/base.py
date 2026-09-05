from collections.abc import Hashable, Sequence
from typing import Protocol, runtime_checkable

import msgspec

from searchtool_gtk.collation import SearchToolCollator


class SearchToolModeConfig(msgspec.Struct):
    class_fqn: str = msgspec.field(name='class')


@runtime_checkable
class SearchToolMode[SearchItem: Hashable](Protocol):
    def get_title(self) -> str:
        ...

    def get_collator(self) -> SearchToolCollator[SearchItem]:
        ...

    def fetch_items(self) -> Sequence[SearchItem]:
        ...

    def get_main_item_label(self, item: SearchItem) -> str:
        ...

    def get_secondary_item_label(self, item: SearchItem) -> str | None:
        ...

    # Record that the item has been selected
    def log_access(self, item: SearchItem) -> None:
        ...

    def activate_item(self, item: SearchItem) -> None:
        ...

    def handle_selection_cancellation(self) -> None:
        ...
