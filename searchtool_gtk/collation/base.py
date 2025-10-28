from typing import Protocol, runtime_checkable


@runtime_checkable
class SearchToolCollator[SearchItem](Protocol):
    def compare(self, a: SearchItem, b: SearchItem) -> int:
        ...

    def match_item(self, item: SearchItem, filter_string: str) -> bool:
        ...
