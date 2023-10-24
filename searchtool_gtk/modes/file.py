from pathlib import Path
from glob import glob
import subprocess

from gi.repository import Gtk

from .path import PathMode


class FileMode(PathMode):
    param_json_schema = {
        'type': 'array',
        'items': {
            'type': 'string'
        }
    }

    globs: list[str]

    def __init__(self, globs: list[str]):
        self.globs = globs
        self.recent = Gtk.RecentManager()

    def fetch_items(self):
        return [Path(path) for pattern in self.globs for path in glob(pattern)]

    def activate_item(self, item: Path):
        subprocess.Popen(['xdg-open', item.as_posix()], start_new_session=True).wait()
