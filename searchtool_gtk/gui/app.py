from collections.abc import Mapping, Sequence
from typing import override

from gi.repository import Adw, Gio, GLib

from ..config import ModeDict
from ..exceptions import SearchToolValidationError
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
    windows: Mapping[str, SearchToolWindow]
    modes: ModeDict

    def __init__(self, modes: ModeDict) -> None:
        super().__init__(application_id='net.ivasilev.SearchToolGTK')

        self.modes = modes
        self.windows = {}

        self.set_accels_for_action('win.select-prev', ['Up'])
        self.set_accels_for_action('win.select-next', ['Down'])
        self.set_accels_for_action('win.minimize', ['Escape'])
        self.set_accels_for_action('win.submit', ['Return'])

    @override
    def run(self, args: list[str] | None) -> int:
        exit_status = super().run(args)

        if exit_status > 0:
            raise SystemExit(exit_status)

        return 0

    @override
    def do_activate(self) -> None:
        self.windows = {
            name: SearchToolWindow(self, name, mode) for name, mode in self.modes.items()
        }

        conn = self.get_dbus_connection()

        if conn is None:
            return

        # Based on https://github.com/rhinstaller/dasbus/blob/be51b94b083bad6fa0716ad6dc97d12f4462f8d4/src/dasbus/server/handler.py#L60
        for interface in Gio.DBusNodeInfo.new_for_xml(DBUS_INTERFACE).interfaces:
            conn.register_object(
                object_path='/net/ivasilev/SearchToolGTK',
                interface_info=interface,
                method_call_closure=self.dbus_callback,
                get_property_closure=None,
                set_property_closure=None
            )

    def dbus_callback(
            self,
            connection: Gio.DBusConnection,
            sender: str,
            object_path: str,
            interface_name: str,
            method_name: str,
            params: GLib.Variant,
            invocation: Gio.DBusMethodInvocation
        ) -> None:

        mode_name: str = params[0]
        window = self.windows.get(mode_name)

        if window is None:
            invocation.return_dbus_error('net.ivasilev.SearchToolGTK.InvalidModeError', f'No mode with name {repr(mode_name)} has been configured')
            return

        match method_name:
            case 'Activate':
                window.activate()
                invocation.return_value()

            case 'Pick':
                items: Sequence[str] = params[1]

                if hasattr(window.mode, 'handle_dbus_input'):
                    window.mode.handle_dbus_input(mode_name, invocation, items)
                else:
                    raise SearchToolValidationError(f'Mode f{mode_name} cannot handle D-Bus input')

                window.activate()
