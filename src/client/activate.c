#include <gio/gio.h>

int main(int argc, const char *argv[])
{
  if (argc != 2) {
    g_printerr("Usage: searchtool-gtk-activate <mode_name>\n");
    return 1;
  }

  GError* error = NULL;
  GDBusConnection *connection = g_bus_get_sync(
    G_BUS_TYPE_SESSION,
    NULL, // GCancellable* cancellable,
    &error
  );

  if (error != NULL) {
    g_printerr("%s\n", error->message);
    g_clear_error(&error);
  }

  g_assert(connection != NULL);
  g_assert(!g_dbus_connection_is_closed(connection));

  GVariant *params = g_variant_new("(s)", argv[1]);
  GVariantType *reply_type = g_variant_type_new("()");

  GVariant *result = g_dbus_connection_call_sync(
    connection,
    "net.ivasilev.SearchToolGTK",
    "/net/ivasilev/SearchToolGTK",
    "net.ivasilev.SearchToolGTK",
    "Activate",
    params,
    reply_type,
    G_DBUS_CALL_FLAGS_NONE,
    -1, // gint timeout_msec,
    NULL, // GCancellable* cancellable,
    &error
  );

  if (error != NULL) {
    g_printerr("%s\n", error->message);
    g_clear_error(&error);
  }

  g_variant_type_free(reply_type);

  if (result != NULL) {
    g_variant_unref(result);
  }

  g_dbus_connection_close_sync(
    connection,
    NULL, // GCancellable* cancellable,
    &error
  );

  if (error != NULL) {
    g_printerr("%s\n", error->message);
    g_clear_error(&error);
  }

  g_object_unref(connection);
  return 0;
}
