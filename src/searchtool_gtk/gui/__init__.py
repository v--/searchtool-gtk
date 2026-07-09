# ruff: file-ignore[non-empty-init-module, module-import-not-at-top-of-file]
import gi


gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from .app import SearchToolApp
from .styling import apply_styling


apply_styling()


__all__ = ['SearchToolApp']
