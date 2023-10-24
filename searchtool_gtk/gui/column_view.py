from typing import Union, Generic, Any

from gi.repository import GObject, Gio, Gtk

from ..mode import SearchToolMode, SearchItem
from .entity import SearchToolEntity, SearchToolEntityWidget


class SearchToolFilter(Gtk.Filter):
    filter_string: str
    mode: SearchToolMode

    def __init__(self, mode: SearchToolMode, filter_string: str):
        super().__init__()
        self.mode = mode
        self.filter_string = filter_string

    def do_match(self, item: Union[GObject.Object, None] = None) -> bool:
        return isinstance(item, SearchToolEntity) and self.mode.match_item(item.si, self.filter_string)


class SearchToolSorter(Gtk.Sorter):
    mode: SearchToolMode

    def __init__(self, mode: SearchToolMode):
        super().__init__()
        self.mode = mode

    def do_compare(self, a: Union[GObject.Object, None] = None, b: Union[GObject.Object, None] = None) -> Gtk.Ordering:
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
    cached_items: list[SearchItem]
    mode: SearchToolMode[SearchItem, Any]

    def __init__(self, title: str, mode: SearchToolMode):
        self.title = title
        self.cached_items = []
        self.mode = mode

        self.store = Gio.ListStore()

        self.filter_model = Gtk.FilterListModel(
            model=self.store,
            incremental=True
        )

        self.sort_model = Gtk.SortListModel(
            model=self.filter_model,
            incremental=True,
            sorter=SearchToolSorter(mode)
        )

        self.selection = Gtk.SingleSelection(model=self.sort_model)

        super().__init__(model=self.selection)

        column_factory = Gtk.SignalListItemFactory()
        column = Gtk.ColumnViewColumn(factory=column_factory, title=title, expand=True)
        column_factory.connect('setup', self.column_setup)
        column_factory.connect('bind', self.column_bind)

        self.append_column(column)

    def column_setup(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell):  # type: ignore
        cell.set_child(SearchToolEntityWidget())

    def column_bind(self, factory: Gtk.SignalListItemFactory, cell: Gtk.ColumnViewCell):  # type: ignore
        item = cell.get_item().si
        widget = cell.get_child()
        widget.main_label.set_markup(self.mode.get_main_item_label(item))
        secondary_text = self.mode.get_secondary_item_label(item)

        if secondary_text is not None:
            widget.secondary_label.set_markup(secondary_text)

    def update_filter_text(self, text: Union[str, None]):
        self.filter_model.set_filter(SearchToolFilter(self.mode, text) if text is not None else None)

    def scroll_to_current(self):
        self.scroll_to(
            pos=self.selection.get_selected() or 0,
            column=None,
            flags=Gtk.ListScrollFlags.NONE,
            scroll=None
        )

    def focus_first(self):
        if self.filter_model.get_property('n_items') > 0:
            self.selection.set_selected(0)
            self.scroll_to_current()

    def focus_prev(self):
        pos = self.selection.get_selected()
        n = self.filter_model.get_property('n_items')

        if n == 0:
            return

        if pos == Gtk.INVALID_LIST_POSITION:
            self.selection.set_selected(n - 1)
        elif pos > 0:
            self.selection.set_selected(pos - 1)

        self.scroll_to_current()

    def focus_next(self):
        pos = self.selection.get_selected()
        n = self.filter_model.get_property('n_items')

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
