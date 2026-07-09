from collections.abc import Hashable, Mapping, Sequence
from typing import override

from gi.repository import Adw, Gio, GLib

from searchtool_gtk.config import ModeMapping

from .window import SearchToolWindow


DBUS_INTERFACE = """<node>
  <error name="net.ivasilev.SearchToolGTK.InvalidModeError">
  </error>

  <interface name="net.ivasilev.SearchToolGTK">
    <method name="Activate">
      <arg direction="in" name="name" type="s"/>
    </method>
    <method name="Pick">
      <arg direction="in" name="name" type="s"/>
      <arg direction="in" name="items" type="as"/>
      <arg direction="out" name="is_selected" type="b"/>
      <arg direction="out" name="item" type="s"/>
    </method>
  </interface>
</node>"""


class SearchToolApp(Adw.Application):
    windows: Mapping[str, SearchToolWindow[Hashable]]
    modes: ModeMapping

    def __init__(self, modes: ModeMapping) -> None:
        super().__init__(application_id='net.ivasilev.SearchToolGTK')

        self.modes = modes
        self.windows = {}

        self.set_accels_for_action('win.select-prev', ['Up'])
        self.set_accels_for_action('win.select-next', ['Down'])
        self.set_accels_for_action('win.minimize', ['Escape'])
        self.set_accels_for_action('win.submit', ['Return'])

    @override
    def do_activate(self) -> None:
        self.windows = {
            name: SearchToolWindow(self, mode) for name, mode in self.modes.items()
        }

        if conn := self.get_dbus_connection():
            for interface in Gio.DBusNodeInfo.new_for_xml(DBUS_INTERFACE).interfaces:
                conn.register_object_with_closures2(
                    object_path='/net/ivasilev/SearchToolGTK',
                    interface_info=interface,
                    method_call_closure=self.dbus_callback,
                )

    def dbus_callback(
        self,
        connection: Gio.DBusConnection,
        sender: str,
        object_path: str,
        interface_name: str,
        method_name: str,
        params: GLib.Variant,
        invocation: Gio.DBusMethodInvocation,
    ) -> None:
        mode_name: str = params[0]
        window = self.windows.get(mode_name)

        if window is None:
            invocation.return_dbus_error('net.ivasilev.SearchToolGTK.InvalidModeError', f'No mode with name {mode_name!r} has been configured')
            return

        match method_name:
            case 'Activate':
                window.activate()
                invocation.return_value()

            case 'Pick':
                items: Sequence[str] = params[1]

                if hasattr(window.mode, 'handle_dbus_input'):
                    window.mode.handle_dbus_input(mode_name, invocation, items)
                    window.activate()
                else:
                    invocation.return_dbus_error('net.ivasilev.SearchToolGTK.InvalidModeError', f'Mode with name {mode_name!r} cannot handle D-Bus input')
