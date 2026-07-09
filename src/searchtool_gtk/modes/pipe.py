from collections.abc import Hashable, Sequence
from typing import override

from gi.repository import Gio, GLib

from searchtool_gtk.exceptions import SearchToolValidationError

from .base import SearchToolMode


class PipeMode[SearchItem: Hashable](SearchToolMode[SearchItem]):
    # The invocation and list are populated on demand by calling the handle_dbus_input method
    invocation: Gio.DBusMethodInvocation | None
    items: Sequence[SearchItem]

    def __init__(self) -> None:
        self.invocation = None
        self.items = []

    @override
    def get_main_item_label(self, item: SearchItem) -> str:
        return str(item)

    @override
    def get_secondary_item_label(self, item: SearchItem) -> str | None:
        return None

    @override
    def fetch_items(self) -> Sequence[SearchItem]:
        return self.items

    def digest_dbus_input(self, items: Sequence[str]) -> None:
        raise NotImplementedError

    def handle_dbus_input(self, mode_name: str, invocation: Gio.DBusMethodInvocation, items: Sequence[str]) -> None:
        if self.invocation:
            invocation.return_dbus_error('net.ivasilev.SearchToolGTK.LockError', 'Another invocation is already processing')
            return

        self.invocation = invocation

        try:
            self.digest_dbus_input(items)
        except NotImplementedError as err:
            raise SearchToolValidationError(f'Mode {mode_name} cannot digest D-Bus input') from err

    @override
    def activate_item(self, item: SearchItem) -> None:
        if self.invocation:
            self.invocation.return_value(
                GLib.Variant('(bs)', [True, str(item)]),
            )

            self.invocation = None

    @override
    def handle_selection_cancellation(self) -> None:
        if self.invocation:
            self.invocation.return_value(
                GLib.Variant('(bs)', [False, '']),
            )

            self.invocation = None
