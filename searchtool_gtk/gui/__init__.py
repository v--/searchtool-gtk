import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from .app import SearchToolApp  # noqa: E402


__all__ = ['SearchToolApp']
