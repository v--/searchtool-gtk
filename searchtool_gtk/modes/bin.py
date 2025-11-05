import os
import pathlib
import subprocess
from collections.abc import Sequence

from gi.repository import Gtk

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

    def fetch_items(self) -> Sequence[pathlib.Path]:
        return [path for d in self.dirs for path in d.iterdir()]

    def activate_item(self, item: pathlib.Path) -> None:
        subprocess.Popen(
            item.as_posix(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
