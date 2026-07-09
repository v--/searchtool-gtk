import sys
from collections.abc import Sequence

from gi.repository import Gio, GLib


def dmenu(mode_name: str, input_data: Sequence[str]) -> int:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: <input> | searchtool-gtk-dmenu <mode_name> | <output>')

    mode_name = sys.argv[1]

    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
    proxy = Gio.DBusProxy.new_sync(
        connection=bus,
        flags=Gio.DBusProxyFlags.NONE,
        info=None,
        name='net.ivasilev.SearchToolGTK',
        object_path='/net/ivasilev/SearchToolGTK',
        interface_name='net.ivasilev.SearchToolGTK',
    )

    try:
        result = proxy.call_sync(
            method_name='Pick',
            parameters=GLib.Variant('(sas)', (mode_name, input_data)),
            flags=Gio.DBusCallFlags.NONE,
            timeout_msec=-1,
        )
    except GLib.Error as err:
        raise SystemExit(str(err)) from err

    if result.get_child_value(0).get_boolean():
        sys.stdout.write(result.get_child_value(1).get_string())
        return 0

    return 1


def dmenu_cli() -> int:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: <input> | searchtool-gtk-dmenu <mode_name> | <output>')

    input_data = [line.rstrip(b'\n').decode('utf-8', errors='ignore') for line in sys.stdin.buffer]
    return dmenu(sys.argv[1], input_data)
