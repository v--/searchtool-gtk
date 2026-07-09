import sys

from gi.repository import Gio, GLib


def activate(mode_name: str) -> int:
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
        proxy.call_sync(
            method_name='Activate',
            parameters=GLib.Variant('(s)', (mode_name,)),
            flags=Gio.DBusCallFlags.NONE,
            timeout_msec=-1,
        )
    except GLib.Error as err:
        raise SystemExit(str(err)) from err

    return 0


def activate_cli() -> int:
    if len(sys.argv) != 2:
        raise SystemExit('Usage: searchtool-gtk-activate <mode_name>')

    return activate(sys.argv[1])
