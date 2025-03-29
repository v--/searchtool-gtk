from typing import Generic, Any, Sequence

from gi.repository import GObject, GLib, Gio, Gtk

from ..mode import SearchToolMode, SearchItem
from .entity import SearchToolEntity, SearchToolEntityWidget


class SearchToolFilter(Gtk.Filter):
    filter_string: str
    mode: SearchToolMode

    def __init__(self, mode: SearchToolMode, filter_string: str):
        super().__init__()
        self.mode = mode
        self.filter_string = filter_string

    def do_match(self, item: GObject.Object | None = None) -> bool:
        return isinstance(item, SearchToolEntity) and self.mode.match_item(item.si, self.filter_string)


class SearchToolSorter(Gtk.Sorter):
    mode: SearchToolMode

    def __init__(self, mode: SearchToolMode):
        super().__init__()
        self.mode = mode

    def do_compare(self, a: GObject.Object | None = None, b: GObject.Object | None = None) -> Gtk.Ordering:
        if not isinstance(a, SearchToolEntity) or not isinstance(b, SearchToolEntity):
            return NotImplemented

        for a_key, b_key in zip(self.mode.get_item_sort_keys(a.si), self.mode.get_item_sort_keys(b.si)):
            if a_key > b_key:
                return Gtk.Ordering.SMALLER

            if a_key < b_key:
                return Gtk.Ordering.LARGER

        return Gtk.Ordering.EQUAL


class SearchToolColumnView(Generic[SearchItem], Gtk.ColumnView):
    store: Gio.ListStore
    filter_model: Gtk.FilterListModel
    sort_model: Gtk.SortListModel
    selection: Gtk.SingleSelection

    title: str
    cached_items: Sequence[SearchItem]
    mode: SearchToolMode[SearchItem, Any]

    def __init__(self, title: str, mode: SearchToolMode):
        self.title = title
        self.cached_items = []
        self.mode = mode

        self.store = Gio.ListStore()
        self.sort_model = Gtk.SortListModel(
            model=self.store,
            incremental=True,
            sorter=SearchToolSorter(mode)
        )

        self.filter_model = Gtk.FilterListModel(
            model=self.sort_model,
            incremental=True
        )

        self.selection = Gtk.SingleSelection(model=self.filter_model)

        super().__init__(model=self.selection)

        self.filter_model.connect('items-changed', self.on_items_changed)

        column_factory = Gtk.SignalListItemFactory()
        column = Gtk.ColumnViewColumn(factory=column_factory, title=title, expand=True)
        column_factory.connect('setup', self.column_setup)
        column_factory.connect('bind', self.column_bind)

        self.append_column(column)

    # This shouldn't be necessary, but I get weird bugs otherwise like a blank ColumnView
    def on_items_changed(self, list_model: Gtk.FilterListModel, pos: int, added: int, removed: int):
        if list_model.get_pending() == 0:
            GLib.idle_add(self.select_first)

    def column_setup(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell):  # type: ignore[name-defined]
        cell.set_child(SearchToolEntityWidget())

    def column_bind(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell):  # type: ignore[name-defined]
        gtk_item = cell.get_item()
        assert isinstance(gtk_item, SearchToolEntity)
        widget = cell.get_child()
        assert isinstance(widget, SearchToolEntityWidget)

        item = gtk_item.si
        widget.main_label.set_label(self.mode.get_main_item_label(item))
        widget.main_label.set_tooltip_text(self.mode.get_main_item_label(item))
        secondary_text = self.mode.get_secondary_item_label(item)

        if secondary_text is None:
            widget.secondary_label.set_visible(False)
        else:
            widget.secondary_label.set_visible(True)
            widget.secondary_label.set_label(secondary_text)

    def update_filter_text(self, text: str | None):
        self.filter_model.set_filter(SearchToolFilter(self.mode, text) if text is not None else None)

    def resort(self):
        # Trigger a resorting
        self.sort_model.set_sorter(SearchToolSorter(self.mode))

    def scroll_to_current(self):
        self.scroll_to(
            pos=self.selection.get_selected() or 0,
            column=None,
            flags=Gtk.ListScrollFlags.NONE,
            scroll=None
        )

    def select_first(self):
        if self.filter_model.get_n_items() > 0:
            self.selection.set_selected(0)
            self.scroll_to_current()

    def select_prev(self):
        pos = self.selection.get_selected()
        n = self.filter_model.get_n_items()

        if n == 0:
            return

        if pos == Gtk.INVALID_LIST_POSITION:
            self.selection.set_selected(0)
        elif pos > 0:
            self.selection.set_selected(pos - 1)

        self.scroll_to_current()

    def select_next(self):
        pos = self.selection.get_selected()
        n = self.filter_model.get_n_items()

        if n == 0:
            return

        if pos == Gtk.INVALID_LIST_POSITION:
            self.selection.set_selected(0)
        elif pos + 1 < n:
            self.selection.set_selected(pos + 1)

        self.scroll_to_current()

    def refresh_options(self):
        new_items = self.mode.fetch_items()

        if self.cached_items == new_items:
            return

        self.cached_items = new_items
        self.store.remove_all()

        for item in new_items:
            self.store.append(SearchToolEntity(item))

        self.scroll_to_current()

    def get_selected(self):
        entity = self.selection.get_selected_item()
        return None if entity is None else entity.si
