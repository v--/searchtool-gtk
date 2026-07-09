import pathlib
import subprocess
import warnings
from collections.abc import Sequence
from typing import override

import icu
import msgspec
import wcmatch.glob

from searchtool_gtk.collation import PathCollator, StringCollator
from searchtool_gtk.exceptions import SearchToolValidationError

from .path import PathMode


def validate_wcmatch_flags(flags: Sequence[str]) -> None:
    for f in flags:
        if not hasattr(wcmatch.glob, f):
            raise SearchToolValidationError(f'Unrecognized wcmatch glob flag {f}')


class FileModeConfig(msgspec.Struct, forbid_unknown_fields=True):
    patterns: Sequence[str]
    wcmatch_flags: Sequence[str] = msgspec.field(default_factory=lambda: ['NEGATE', 'GLOBSTAR', 'BRACE', 'GLOBTILDE'])
    icu_locale: str | None = None
    icu_strength: int = icu.Collator.PRIMARY


class FileMode(PathMode):
    __searchtool_config_type__ = FileModeConfig
    config: FileModeConfig

    def __init__(self, config: FileModeConfig) -> None:
        super().__init__()
        self.config = config

    @override
    def get_collator(self) -> PathCollator:
        return PathCollator(
            self.journal,
            StringCollator(self.config.icu_locale, self.config.icu_strength),
        )

    @override
    def fetch_items(self) -> Sequence[pathlib.Path]:
        flags = sum(getattr(wcmatch.glob, f) for f in self.config.wcmatch_flags)

        return [
            pathlib.Path(path)
            for path in wcmatch.glob.iglob(self.config.patterns, flags=flags)
        ]

    @override
    def activate_item(self, item: pathlib.Path) -> None:
        with warnings.catch_warnings(category=ResourceWarning, record=True):
            subprocess.Popen(['xdg-open', item.as_posix()], start_new_session=True)

        self.journal.log_access(item)
