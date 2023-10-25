from typing import Protocol, TypeVar, runtime_checkable

from referencing.jsonschema import Schema


SearchItem = TypeVar('SearchItem')
SearchItemSortKeys = TypeVar('SearchItemSortKeys', covariant=True)


@runtime_checkable
class SearchToolMode(Protocol[SearchItem, SearchItemSortKeys]):
    @classmethod
    def get_param_json_schema(Cls) -> Schema:
        ...

    def fetch_items(self) -> list[SearchItem]:
        ...

    def get_main_item_label(self, item: SearchItem) -> str:
        ...

    def get_secondary_item_label(self, item: SearchItem) -> str:
        ...

    def get_item_sort_keys(self, item: SearchItem) -> SearchItemSortKeys:
        ...

    def match_item(self, item: SearchItem, filter_string: str) -> bool:
        ...

    # Record that the item has been selected
    def bump_item(self, item: SearchItem):
        ...

    def activate_item(self, item: SearchItem):
        ...
