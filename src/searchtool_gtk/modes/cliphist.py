import contextlib
from collections.abc import Iterable, Sequence
from typing import override

import msgspec

from searchtool_gtk.collation import ClipHistCollator, ClipHistItem, StringCollator

from .pipe import PipeMode


class ClipHistModeConfig(msgspec.Struct, forbid_unknown_fields=True):
    icu_locale: str | None = None
    icu_strength: int = 0


def iter_cliphist_items(strings: Sequence[str]) -> Iterable[ClipHistItem]:
    for string in strings:
        try:
            i, text = string.split('\t', maxsplit=1)
        except ValueError:
            pass
        else:
            with contextlib.suppress(ValueError):
                yield ClipHistItem(int(i), text)


class ClipHistMode(PipeMode[ClipHistItem, ClipHistModeConfig]):
    config: ClipHistModeConfig

    @classmethod
    def build_param_class(cls, param: object) -> ClipHistModeConfig:
        if param is None:
            return ClipHistModeConfig()

        return msgspec.convert(param, type=ClipHistModeConfig)

    @override
    def digest_dbus_input(self, items: Sequence[str]) -> None:
        self.items = list(iter_cliphist_items(items))

    def __init__(self, config: ClipHistModeConfig) -> None:
        super().__init__()
        self.config = config

    @override
    def get_collator(self) -> ClipHistCollator:
        return ClipHistCollator(
            StringCollator(self.config.icu_locale, self.config.icu_strength),
        )

    @override
    def get_main_item_label(self, item: ClipHistItem) -> str:
        return item.value

    @override
    def get_secondary_item_label(self, item: ClipHistItem) -> str:
        return f'id {item.id}'
