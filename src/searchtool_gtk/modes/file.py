import os.path
import pathlib
import subprocess
from collections.abc import Iterable, Sequence
from glob import iglob
from typing import override

import icu
from gi.repository import Gtk

from searchtool_gtk.collation import PathCollator, StringCollator
from searchtool_gtk.pydantic_helpers import StrictPydanticModel
from searchtool_gtk.support.iteration import list_accumulator

from .path import PathMode


class FileModePattern(StrictPydanticModel):
    glob: str
    include_hidden: bool = False
    recursive: bool = False


class FileModeConfig(StrictPydanticModel):
    patterns: Sequence[str | FileModePattern]
    icu_locale: str | None = None
    icu_strength: int = icu.Collator.PRIMARY


class FileMode(PathMode[FileModeConfig]):
    config: FileModeConfig

    @classmethod
    def build_param_class(cls, param: object) -> FileModeConfig:
        return FileModeConfig.model_validate(param)

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
            if isinstance(pattern, FileModePattern):
                it = iglob(
                    pathname=os.path.expanduser(pattern.glob),
                    recursive=pattern.recursive,
                    include_hidden=pattern.include_hidden,
                )
            else:
                it = iglob(pathname=os.path.expanduser(pattern))

            for path in it:
                yield pathlib.Path(path)

    @override
    def activate_item(self, item: pathlib.Path) -> None:
        subprocess.Popen(
            ['xdg-open', item.as_posix()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
