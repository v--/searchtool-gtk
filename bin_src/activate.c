#include <stdio.h>

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

  GVariant *mode_param = g_variant_new_string(argv[1]);
  GVariant *params = g_variant_new_tuple(&mode_param, 1);

  g_dbus_connection_call_sync(
    connection,
    "net.ivasilev.SearchToolGTK",
    "/net/ivasilev/SearchToolGTK",
    "net.ivasilev.SearchToolGTK",
    "Activate",
    params,
    NULL, // const GVariantType* reply_type,
    G_DBUS_CALL_FLAGS_NONE,
    -1, // gint timeout_msec,
    NULL, // GCancellable* cancellable,
    &error
  );

  if (error != NULL) {
    g_printerr("%s\n", error->message);
    g_clear_error(&error);
  }

  g_dbus_connection_close_sync(
    connection,
    NULL, // GCancellable* cancellable,
    &error
  );

  if (error != NULL) {
    g_printerr("%s\n", error->message);
    g_error_free(error);
  }

  return 0;
}
