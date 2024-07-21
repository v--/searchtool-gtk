from pathlib import Path
from glob import glob
import subprocess

from gi.repository import Gtk

from .path import PathMode


class FileMode(PathMode):
    @classmethod
    def get_param_json_schema(Cls):
        return {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'glob': { 'type': 'string' },
                    'include_hidden': { 'type': 'boolean' },
                    'recursive': { 'type': 'boolean' }
                },
                'optionalProperties': ['include_hidden', 'recursive']
            }
        }

    globs: list[str]

    def __init__(self, globs: list[str]):
        self.globs = globs
        self.recent = Gtk.RecentManager()

    def fetch_items(self):
        return [
            Path(path)
            for pattern in self.globs
            for path in glob(
                pathname=pattern['glob'],
                recursive=pattern['recursive'] or False,
                include_hidden=pattern['include_hidden'] or False
            )
        ]

    def activate_item(self, item: Path):
        subprocess.Popen(
            ['xdg-open', item.as_posix()],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
