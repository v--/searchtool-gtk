from pathlib import Path
import os
import subprocess

from gi.repository import Gtk

from .path import PathMode


class BinMode(PathMode):
    param_json_schema = {
        'type': 'null'
    }

    dirs: list[Path]
    recent: Gtk.RecentManager

    def __init__(self, params: None):
        self.dirs = [Path(d) for d in os.environ['PATH'].split(':')]
        self.recent = Gtk.RecentManager()

    def fetch_items(self):
        return [path for d in self.dirs for path in d.iterdir()]

    def activate_item(self, item: Path):
        subprocess.Popen(item.as_posix(), start_new_session=True).wait()
