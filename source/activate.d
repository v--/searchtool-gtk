import std.stdio: stderr;

import gio.DBusConnection;
import glib.Variant;
import glib.VariantType;

int main(string[] args)
{
    if (args.length != 2) {
        stderr.writeln("Usage: searchtool-gtk-activate <mode_name>");
        return 1;
    }

    string modeName = args[1];

    auto conn = DBusConnection.getSync(GBusType.SESSION, null);
    conn.callSync(
        "net.ivasilev.SearchToolGTK",
        "/net/ivasilev/SearchToolGTK",
        "net.ivasilev.SearchToolGTK",
        "Activate",
        new Variant([new Variant(modeName)]),
        null, // Return type
        GDBusCallFlags.NONE,
        MAXINT32, // Timeout
        null // Cancellable
    );

    return 0;
}
