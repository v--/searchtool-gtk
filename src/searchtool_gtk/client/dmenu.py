import sys

from gi.repository import Gio, GLib


def dmenu_client() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: <input> | searchtool-gtk-dmenu <mode_name> | <output>\n')

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

    input_data = [line.rstrip('\n') for line in sys.stdin]
    result = proxy.call_sync(
        method_name='Pick',
        parameters=GLib.Variant('(sas)', (mode_name, input_data)),
        flags=Gio.DBusCallFlags.NONE,
        timeout_msec=-1,
    )

    if result.get_child_value(0).get_boolean():
        sys.stdout.write(result.get_child_value(1).get_string())
        sys.exit(0)

    sys.exit(1)
