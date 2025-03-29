from collections.abc import Sequence
from typing import Any

from pathlib import Path
from glob import glob
import subprocess


from gi.repository import Gtk

from .path import PathMode
from ..matching import mangle
from ..pydantic_helpers import StrictPydanticModel


class FileModePattern(StrictPydanticModel):
    glob: str
    include_hidden: bool = False
    recursive: bool = False


class FileModeConfig(StrictPydanticModel):
    patterns: Sequence[FileModePattern]
    loose_matching: bool = False


class FileMode(PathMode):
    config: FileModeConfig

    @classmethod
    def build_param_class(cls, param: Any) -> FileModeConfig:
        return FileModeConfig.model_validate(param)

    def __init__(self, config: FileModeConfig):
        self.config = config
        self.recent = Gtk.RecentManager()

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

    def match_item(self, item: Path, filter_string: str):
        if self.config.loose_matching:
            return mangle(filter_string) in mangle(item.as_posix())

        return super().match_item(item, filter_string)

    def activate_item(self, item: Path):
        subprocess.Popen(
            ['xdg-open', item.as_posix()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
