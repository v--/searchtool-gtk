from typing import Generic

from gi.repository import GObject, Gtk, Pango

from ..mode import SearchItem


class SearchToolEntity(Generic[SearchItem], GObject.Object):
    si: SearchItem

    def __init__(self, si: SearchItem):
        super().__init__()
        self.si = si


class SearchToolEntityWidget(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.main_label = Gtk.Label(halign=Gtk.Align.START, ellipsize=Pango.EllipsizeMode.MIDDLE)
        self.append(self.main_label)

        self.secondary_label = Gtk.Label(halign=Gtk.Align.START)
        self.secondary_label.add_css_class('secondary')
        self.append(self.secondary_label)
