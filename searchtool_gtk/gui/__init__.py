import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from .app import SearchToolApp  # noqa: E402
from .styling import apply_styling  # noqa: E402


apply_styling()


__all__ = ['SearchToolApp']
