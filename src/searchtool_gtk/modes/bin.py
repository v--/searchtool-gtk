import contextlib
import os
import pathlib
import subprocess
import warnings
from collections.abc import Iterable, Sequence
from typing import override

from .path import PathMode


class BinMode(PathMode):
    dirs: Sequence[pathlib.Path]

    def __init__(self) -> None:
        super().__init__()
        self.dirs = [pathlib.Path(d) for d in os.environ['PATH'].split(':')]

    def get_title(self) -> str:
        return 'Binaries'

    def iter_items(self) -> Iterable[pathlib.Path]:
        for dir_ in self.dirs:
            with contextlib.suppress(FileNotFoundError):
                yield from dir_.iterdir()

    @override
    def fetch_items(self) -> Sequence[pathlib.Path]:
        return list(self.iter_items())

    @override
    def activate_item(self, item: pathlib.Path) -> None:
        with warnings.catch_warnings(category=ResourceWarning, record=True):
            subprocess.Popen(item.as_posix(), start_new_session=True)

        self.journal.log_access(item)
        print(item, self.journal.get_last_access(item))
