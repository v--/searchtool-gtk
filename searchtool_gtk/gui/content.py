from typing import Union

from gi.repository import GObject, Gtk

from ..config import SearchToolConfigItem
from .column_view import SearchToolColumnView


GUI_WIDTH = 800
GUI_HEIGHT = 400
GUI_SPACING = 20


class SearchToolContent(Gtk.Box):
    scroll_box: Gtk.ScrolledWindow
    outer_box: Gtk.Box
    submit_button: Gtk.Button
    input_widget: Gtk.Entry
    config_list: list[SearchToolConfigItem]
    column_views: list[SearchToolColumnView]
    active: int

    def __init__(self, config_list: list[SearchToolConfigItem]):
        super().__init__()

        self.outer_box = Gtk.Box()
        self.outer_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.append(self.outer_box)

        self.input_widget = Gtk.Entry()
        self.input_widget.connect('changed', self.on_input)

        self.search_bar = Gtk.SearchBar(search_mode_enabled=True)
        self.search_bar.set_child(self.input_widget)
        self.outer_box.append(self.search_bar)

        self.scroll_box = Gtk.ScrolledWindow()
        self.scroll_box.set_min_content_width(GUI_WIDTH)
        self.scroll_box.set_min_content_height(GUI_HEIGHT)
        self.outer_box.append(self.scroll_box)

        self.column_views = [
            SearchToolColumnView(config.name, config.mode_class(config.mode_params)) for config in config_list
        ]

        self.set_active(0)

    @property
    def column_view(self):
        return self.column_views[self.active_index]

    def on_input(self, widget: Gtk.Entry):
        filter_text = widget.get_property('text')
        self.column_view.update_filter_text(filter_text or None)

    def on_select(self, widget: Gtk.Entry):
        self.select()

    def refresh_options(self):
        self.column_view.refresh_options()

    def set_active(self, i: int):
        self.scroll_box.set_child(self.column_views[i])
        self.active_index = i
        self.focus_first()

    def focus_first(self):
        self.column_view.focus_first()

    def focus_prev(self):
        self.column_view.focus_prev()

    def focus_next(self):
        self.column_view.focus_next()

    def reset_search(self):
        self.search_bar.set_search_mode(False)
        self.search_bar.set_search_mode(True)
        self.focus_first()

    def set_key_capture_widget(self, widget: Union[Gtk.Widget, None]):
        self.search_bar.set_key_capture_widget(widget)

    def select(self):
        selected = self.column_view.get_selected()

        if selected is None:
            return

        self.reset_search()
        self.column_view.mode.bump_item(selected)
        self.column_view.mode.activate_item(selected)
        self.emit('submit', self.active_index, selected)


GObject.signal_new(
    'submit',
    SearchToolContent,
    0,
    GObject.TYPE_NONE,
    [GObject.TYPE_INT, GObject.TYPE_PYOBJECT]
)
