import sys

from gi.repository import Gio, GLib


def basic_client() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write('Usage: searchtool-gtk-activate <mode_name>\n')

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

    proxy.call_sync(
        method_name='Activate',
        parameters=GLib.Variant('(s)', (mode_name,)),
        flags=Gio.DBusCallFlags.NONE,
        timeout_msec=-1,
    )
