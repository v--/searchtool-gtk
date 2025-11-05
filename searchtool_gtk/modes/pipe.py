from collections.abc import Sequence
from typing import Any, override

from gi.repository import Gio, GLib

from ..collation import SearchToolCollator, StringCollator
from ..exceptions import SearchToolValidationError
from .base import SearchToolMode


# This is an abstract base class for several real modes
class PipeMode[SearchItem = Any, ParamClass = Any](SearchToolMode[SearchItem, ParamClass]):
    # The invocation and list are populated on demand by calling the handle_dbus_input method
    invocation: Gio.DBusMethodInvocation | None
    items: Sequence[SearchItem]

    def __init__(self) -> None:
        self.invocation = None
        self.items = []

    @override
    def get_collator(self) -> SearchToolCollator:
        return StringCollator()

    @override
    def get_main_item_label(self, item: SearchItem) -> str:
        return str(item)

    @override
    def get_secondary_item_label(self, item: SearchItem) -> str:
        return ''

    @override
    def fetch_items(self) -> Sequence[SearchItem]:
        return self.items

    def digest_dbus_input(self, items: Sequence[str]) -> None:
        raise NotImplementedError

    def handle_dbus_input(self, mode_name: str, invocation: Gio.DBusMethodInvocation, items: Sequence[str]) -> None:
        self.invocation = invocation

        try:
            self.digest_dbus_input(items)
        except NotImplementedError as err:
            raise SearchToolValidationError(f'Mode f{mode_name} cannot digest D-Bus input') from err

    # Items should be bumped by whatever piped them
    @override
    def bump_item(self, item: SearchItem) -> None:
        pass

    @override
    def activate_item(self, item: SearchItem) -> None:
        if self.invocation is not None:
            self.invocation.return_value(
                GLib.Variant('(bs)', [True, str(item)])
            )

            self.invocation = None

    @override
    def handle_selection_cancellation(self) -> None:
        if self.invocation is not None:
            self.invocation.return_value(
                GLib.Variant('(bs)', [False, ''])
            )

            self.invocation = None
