from collections.abc import Sequence
from typing import Any, override

from gi.repository import Gio, GLib

from ..collation import StringCollator
from .base import SearchToolMode


# This is an abstract base class for several real modes
class PipeMode[ParamClass = Any](SearchToolMode[str, ParamClass]):
    # The invocation and list are populated on demand by calling the handle_dbus_input method
    invocation: Gio.DBusMethodInvocation | None
    items: Sequence[str]

    def __init__(self):
        self.invocation = None
        self.items = []

    @override
    def get_collator(self) -> StringCollator:
        return StringCollator()

    @override
    def get_main_item_label(self, item: str):
        return item

    @override
    def get_secondary_item_label(self, item: str):
        return None

    @override
    def fetch_items(self):
        return self.items

    def handle_dbus_input(self, invocation: Gio.DBusMethodInvocation, items: Sequence[str]):
        self.invocation = invocation
        self.items = items

    # Items should be bumped by whatever piped them
    @override
    def bump_item(self, item: str):
        pass

    @override
    def activate_item(self, item: str):
        if self.invocation is not None:
            self.invocation.return_value(
                GLib.Variant('(bs)', [True, item])
            )

            self.invocation = None

    @override
    def handle_selection_cancellation(self):
        if self.invocation is not None:
            self.invocation.return_value(
                GLib.Variant('(bs)', [False, ''])
            )

            self.invocation = None
