import os
import pathlib
import subprocess
from collections.abc import Iterable, Sequence
from enum import StrEnum
from typing import override

from gi.repository import Gtk

from ..pydantic_helpers import StrictPydanticModel
from ..support.iteration import list_accumulator
from .path import PathMode


class BinModeStreamOption(StrEnum):
    DEVNULL = 'DEVNULL'
    INHERIT = 'INHERIT'

    def get_descriptor(self) -> int | None:
        match self:
            case BinModeStreamOption.INHERIT:
                return None

            case BinModeStreamOption.DEVNULL:
                return subprocess.DEVNULL


class BinModeConfig(StrictPydanticModel):
    stdout: BinModeStreamOption = BinModeStreamOption.DEVNULL
    stderr: BinModeStreamOption = BinModeStreamOption.DEVNULL


class BinMode(PathMode[BinModeConfig]):
    dirs: Sequence[pathlib.Path]
    recent: Gtk.RecentManager
    config: BinModeConfig

    @classmethod
    def build_param_class(cls, param: object) -> BinModeConfig:
        return BinModeConfig.model_validate(param)

    def __init__(self, config: BinModeConfig) -> None:
        self.dirs = [pathlib.Path(d) for d in os.environ['PATH'].split(':')]
        self.recent = Gtk.RecentManager()
        self.config = config

    @override
    @list_accumulator
    def fetch_items(self) -> Iterable[pathlib.Path]:
        for dir_ in self.dirs:
            try:
                yield from dir_.iterdir()
            except FileNotFoundError:
                pass

    @override
    def activate_item(self, item: pathlib.Path) -> None:
        subprocess.Popen(
            item.as_posix(),
            stdout=self.config.stdout.get_descriptor(),
            stderr=self.config.stderr.get_descriptor(),
            start_new_session=True
        )
