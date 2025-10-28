from collections.abc import Sequence
from pathlib import Path
import os
import subprocess

from gi.repository import Gtk

from .path import PathMode


class BinMode(PathMode):
    dirs: Sequence[Path]
    recent: Gtk.RecentManager

    @classmethod
    def build_param_class(cls, param: None) -> None:
        return None

    def __init__(self):
        self.dirs = [Path(d) for d in os.environ['PATH'].split(':')]
        self.recent = Gtk.RecentManager()

    def fetch_items(self):
        return [path for d in self.dirs for path in d.iterdir()]

    def activate_item(self, item: Path):
        subprocess.Popen(
            item.as_posix(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
