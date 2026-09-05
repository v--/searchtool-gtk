import subprocess
from collections.abc import Sequence
from typing import override

import msgspec

from searchtool_gtk.collation import ClipHistCollator, ClipHistItem, StringCollator

from .cliphist import iter_cliphist_items
from .pipe import PipeMode


class ClipHistModeConfig(msgspec.Struct, forbid_unknown_fields=True):
    icu_locale: str | None = None
    icu_strength: int = 0
    prime: bool = False


class ClipHistLegacyMode(PipeMode[ClipHistItem]):
    __searchtool_config_type__ = ClipHistModeConfig
    config: ClipHistModeConfig

    # We ignore the journal because access should be logger by cliphist
    def __init__(self, config: ClipHistModeConfig) -> None:
        super().__init__()
        self.config = config

    @override
    def digest_dbus_input(self, items: Sequence[str]) -> None:
        self.items = list(iter_cliphist_items(items))

    @override
    def get_title(self) -> str:
        return 'Clipboard history'

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

    def prime_items(self) -> Sequence[ClipHistItem]:
        if not self.config.prime:
            return []

        proc = subprocess.run(
            ['cliphist', 'list'],
            stdout=subprocess.PIPE,
            encoding='utf-8',
            check=True,
        )

        return list(iter_cliphist_items(proc.stdout.splitlines()))
