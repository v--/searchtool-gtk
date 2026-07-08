from collections.abc import Hashable, Sequence
from typing import Protocol, Self, runtime_checkable

from searchtool_gtk.collation import SearchToolCollator


@runtime_checkable
class SearchToolMode[SearchItem: Hashable](Protocol):
    @classmethod
    def from_config(cls, param: object) -> Self:
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
    def bump_item(self, item: SearchItem) -> None:
        ...

    def activate_item(self, item: SearchItem) -> None:
        ...

    def handle_selection_cancellation(self) -> None:
        ...
