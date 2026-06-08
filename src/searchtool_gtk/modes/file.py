import os.path
import pathlib
import subprocess
import warnings
from collections.abc import Iterable, Iterator, Sequence
from glob import iglob
from typing import override

import icu
import msgspec
import wcmatch.glob
from gi.repository import Gtk

from searchtool_gtk.collation import PathCollator, StringCollator
from searchtool_gtk.exceptions import SearchToolDeprecationWarning, SearchToolIntegrityError, SearchToolValidationError
from searchtool_gtk.support.iteration import list_accumulator

from .path import PathMode


def validate_wcmatch_flags(flags: Sequence[str]) -> None:
    for f in flags:
        if not hasattr(wcmatch.glob, f):
            raise SearchToolValidationError(f'Unrecognized wcmatch glob flag {f}')


class LegacyFileModePattern(msgspec.Struct, forbid_unknown_fields=True):
    glob: str
    include_hidden: bool = False
    recursive: bool = False


class FileModeConfig(msgspec.Struct, forbid_unknown_fields=True):
    patterns: Sequence[str | LegacyFileModePattern]
    use_wcmatch: bool
    wcmatch_flags: Sequence[str] = msgspec.field(default_factory=lambda: ['NEGATE', 'GLOBSTAR', 'BRACE', 'GLOBTILDE'])
    icu_locale: str | None = None
    icu_strength: int = icu.Collator.PRIMARY


class FileMode(PathMode[FileModeConfig]):
    config: FileModeConfig

    @classmethod
    def build_param_class(cls, param: object) -> FileModeConfig:
        config = msgspec.convert(param, type=FileModeConfig)

        if config.use_wcmatch:
            validate_wcmatch_flags(config.wcmatch_flags)

            for pattern in config.patterns:
                if isinstance(pattern, LegacyFileModePattern):
                    raise SearchToolValidationError('Invalid legacy object-based pattern for wcmatch')
        else:
            warnings.warn(
                SearchToolDeprecationWarning('stdlib globs are deprecated; consider enabling `use_wcmatch`'),
                stacklevel=2,
            )

        return config

    def __init__(self, config: FileModeConfig) -> None:
        self.config = config
        self.recent = Gtk.RecentManager()

    @override
    def get_collator(self) -> PathCollator:
        return PathCollator(
            self.recent,
            StringCollator(self.config.icu_locale, self.config.icu_strength),
        )

    @override
    @list_accumulator
    def fetch_items(self) -> Iterable[pathlib.Path]:
        for pattern in self.config.patterns:
            it: Iterator[str]

            if isinstance(pattern, LegacyFileModePattern):
                if self.config.use_wcmatch:
                    raise SearchToolIntegrityError('Invalid legacy object-based pattern for wcmatch')

                it = iglob(
                    pathname=os.path.expanduser(pattern.glob),
                    recursive=pattern.recursive,
                    include_hidden=pattern.include_hidden,
                )
            elif self.config.use_wcmatch:
                flags = sum(getattr(wcmatch.glob, f) for f in self.config.wcmatch_flags)
                it = wcmatch.glob.iglob(pattern, flags=flags)
            else:
                it = iglob(pathname=os.path.expanduser(pattern))

            for path in it:
                yield pathlib.Path(path)

    @override
    def activate_item(self, item: pathlib.Path) -> None:
        with warnings.catch_warnings(category=ResourceWarning, record=True):
            subprocess.Popen(
                ['xdg-open', item.as_posix()],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
