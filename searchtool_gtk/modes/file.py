import subprocess
from collections.abc import Sequence
from glob import glob
from pathlib import Path
from typing import override

import icu
from gi.repository import Gtk

from ..collation import PathCollator, StringCollator
from ..pydantic_helpers import StrictPydanticModel
from .path import PathMode


class FileModePattern(StrictPydanticModel):
    glob: str
    include_hidden: bool = False
    recursive: bool = False


class FileModeConfig(StrictPydanticModel):
    patterns: Sequence[FileModePattern]
    icu_locale: str | None = None
    icu_strength: int = icu.Collator.PRIMARY


class FileMode(PathMode):
    config: FileModeConfig

    @classmethod
    def build_param_class(cls, param: object) -> FileModeConfig:
        return FileModeConfig.model_validate(param)

    def __init__(self, config: FileModeConfig):
        self.config = config
        self.recent = Gtk.RecentManager()

    @override
    def get_collator(self) -> PathCollator:
        return PathCollator(
            self.recent,
            StringCollator(self.config.icu_locale, self.config.icu_strength)
        )

    @override
    def fetch_items(self):
        return [
            Path(path)
            for pattern in self.config.patterns
            for path in glob(
                pathname=pattern.glob,
                recursive=pattern.recursive,
                include_hidden=pattern.include_hidden
            )
        ]

    @override
    def activate_item(self, item: Path):
        subprocess.Popen(
            ['xdg-open', item.as_posix()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
