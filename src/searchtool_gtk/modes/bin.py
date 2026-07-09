import contextlib
import os
import pathlib
import subprocess
import warnings
from collections.abc import Iterable, Sequence
from enum import StrEnum
from typing import override

import msgspec

from searchtool_gtk.support.iteration import list_accumulator

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


class BinModeConfig(msgspec.Struct, forbid_unknown_fields=True):
    stdout: BinModeStreamOption = BinModeStreamOption.DEVNULL
    stderr: BinModeStreamOption = BinModeStreamOption.DEVNULL


class BinMode(PathMode):
    __searchtool_config_type__ = BinModeConfig

    config: BinModeConfig
    dirs: Sequence[pathlib.Path]

    def __init__(self, config: BinModeConfig) -> None:
        super().__init__()
        self.config = config
        self.dirs = [pathlib.Path(d) for d in os.environ['PATH'].split(':')]

    @override
    @list_accumulator
    def fetch_items(self) -> Iterable[pathlib.Path]:
        for dir_ in self.dirs:
            with contextlib.suppress(FileNotFoundError):
                yield from dir_.iterdir()

    @override
    def activate_item(self, item: pathlib.Path) -> None:
        with warnings.catch_warnings(category=ResourceWarning, record=True):
            subprocess.Popen(
                item.as_posix(),
                stdout=self.config.stdout.get_descriptor(),
                stderr=self.config.stderr.get_descriptor(),
                start_new_session=True,
            )

        self.journal.log_access(item)
        print(item, self.journal.get_last_access(item))
