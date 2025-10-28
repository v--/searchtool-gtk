from typing import Any, Protocol, runtime_checkable

from ..collation import SearchToolCollator


@runtime_checkable
class SearchToolMode[SearchItem = Any, ParamClass = Any](Protocol):
    @classmethod
    def build_param_class(cls, param: object) -> ParamClass:
        ...

    def get_collator(cls) -> SearchToolCollator:
        ...

    def fetch_items(self) -> list[SearchItem]:
        ...

    def get_main_item_label(self, item: SearchItem) -> str:
        ...

    def get_secondary_item_label(self, item: SearchItem) -> str:
        ...

    # Record that the item has been selected
    def bump_item(self, item: SearchItem):
        ...

    def activate_item(self, item: SearchItem):
        ...

    def handle_selection_cancellation(self):
        ...
