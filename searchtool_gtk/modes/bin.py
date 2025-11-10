import os
import pathlib
import subprocess
from collections.abc import Iterable, Sequence
from typing import override

from gi.repository import Gtk

from ..support.iteration import list_accumulator
from .path import PathMode


class BinMode(PathMode[None]):
    dirs: Sequence[pathlib.Path]
    recent: Gtk.RecentManager

    @classmethod
    def build_param_class(cls, param: object) -> None:
        return None

    def __init__(self) -> None:
        self.dirs = [pathlib.Path(d) for d in os.environ['PATH'].split(':')]
        self.recent = Gtk.RecentManager()

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
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
