from gi.repository import Gio, GLib

from ..mode import SearchToolMode


# This is an abstract base class for several real modes
class PipeMode(SearchToolMode[str, tuple[()]]):
    # The invocation and list are populated on demand by calling the handle_dbus_input method
    invocation: Gio.DBusMethodInvocation | None
    items: list[str]

    @classmethod
    def get_param_json_schema(Cls):
        return {
            'type': 'null',
        }

    def __init__(self, params: None):
        self.invocation = None
        self.items = []

    def get_main_item_label(self, item: str):
        return item

    def get_secondary_item_label(self, item: str):
        return None

    def get_item_sort_keys(self, item: str):
        return tuple()

    def match_item(self, item: str, filter_string: str):
        return filter_string.casefold() in item.casefold()

    def fetch_items(self):
        return self.items

    def handle_dbus_input(self, invocation: Gio.DBusMethodInvocation, items: list[str]):
        self.invocation = invocation
        self.items = items

    # Items should be bumped by whatever piped them
    def bump_item(self, item: str):
        pass

    def activate_item(self, item: str):
        if self.invocation is not None:
            self.invocation.return_value(
                GLib.Variant('(bs)', [True, item])
            )

            self.invocation = None

    def handle_selection_cancellation(self):
        if self.invocation is not None:
            self.invocation.return_value(
                GLib.Variant('(bs)', [False, ''])
            )

            self.invocation = None
