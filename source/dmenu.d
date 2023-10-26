import std.algorithm: map;
import std.array: array;
import std.conv: to;
import std.stdio: stdin, stdout, stderr;

import gio.DBusConnection;
import glib.Variant;
import glib.VariantType;

int main(string[] args)
{
    if (args.length != 2) {
        stderr.writeln("Usage: <input> | searchtool-gtk-dmenu <mode_name> | <output>");
        return 1;
    }

    string modeName = args[1];
    string[] items = stdin.byLineCopy.map!(line => line.to!string).array();

    auto conn = DBusConnection.getSync(GBusType.SESSION, null);
    auto result = conn.callSync(
        "net.ivasilev.SearchToolGTK",
        "/net/ivasilev/SearchToolGTK",
        "net.ivasilev.SearchToolGTK",
        "Pick",
        new Variant([
            new Variant(modeName),
            new Variant(items)
        ]),
        new VariantType("(bs)"),
        GDBusCallFlags.NONE,
        MAXINT32, // Timeout
        null // Cancellable
    );

    const isSelected = result.getChildValue(0).getBoolean();

    if (isSelected) {
        ulong strlen;
        const item = result.getChildValue(1).getString(strlen);
        stdout.write(item);
        return 0;
    } else {
        return 1;
    }
}
