from gi.repository import Gtk

from ..modes import SearchToolMode
from .column_view import SearchToolColumnView

GUI_WIDTH = 800
GUI_HEIGHT = 400
GUI_SPACING = 20


class SearchToolContent(Gtk.Box):
    scroll_box: Gtk.ScrolledWindow
    outer_box: Gtk.Box
    submit_button: Gtk.Button
    input_widget: Gtk.Entry
    column_view: SearchToolColumnView

    mode_name: str
    mode: SearchToolMode

    def __init__(self, mode_name: str, mode: SearchToolMode):
        super().__init__()

        self.mode_name = mode_name
        self.mode = mode

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

        self.column_view = SearchToolColumnView(mode_name, mode)
        self.scroll_box.set_child(self.column_view)

    def on_input(self, widget: Gtk.Entry):
        filter_text = widget.get_property('text')
        self.column_view.update_filter_text(filter_text or None)

    def refresh_options(self):
        self.column_view.refresh_options()

    def select_prev(self):
        self.column_view.select_prev()

    def select_next(self):
        self.column_view.select_next()

    def reset_search(self):
        self.input_widget.set_text('')
        self.column_view.resort()

    def set_key_capture_widget(self, widget: Gtk.Widget | None):
        self.search_bar.set_key_capture_widget(widget)

    def get_selected(self):
        return self.column_view.get_selected()
