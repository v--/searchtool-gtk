#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#include <gio/gio.h>

void read_items_from_stdin(GVariantBuilder* items_builder) {
  gchar *line = NULL;
  gchar *unicode_line = NULL;
  size_t len = 0; // This will not be used by getline because <line> will be initialized to NULL, but is required
  ssize_t line_size = 0;

  while (TRUE) {
    line = NULL;
    line_size = getline(&line, &len, stdin);

    if (line_size == -1) {
      switch (errno) {
      case ENOMEM:
        g_printerr("Cannot allocate enough memory to read everything from STDIN.\n");
        return;
      default:
        return;
      }
    }

    unicode_line = g_utf8_make_valid(line, line[line_size - 1] == '\n' ? line_size - 1 : line_size);
    free(line);

    GVariant* line_variant = g_variant_new_string(unicode_line);
    g_variant_builder_add_value(items_builder, line_variant);

    free(unicode_line);
  }
}

int main(gint argc, const gchar *argv[])
{
  if (argc != 2) {
    g_printerr("Usage: <input> | searchtool-gtk-dmenu <mode_name> | <output>\n");
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

  GVariantBuilder items_builder;
  g_variant_builder_init(&items_builder, G_VARIANT_TYPE_ARRAY);
  read_items_from_stdin(&items_builder);

  GVariant *param_array[2];
  param_array[0] = g_variant_new_string(argv[1]);
  param_array[1] = g_variant_builder_end(&items_builder);
  GVariant *params = g_variant_new_tuple(param_array, 2);

  GVariant *result = g_dbus_connection_call_sync(
    connection,
    "net.ivasilev.SearchToolGTK",
    "/net/ivasilev/SearchToolGTK",
    "net.ivasilev.SearchToolGTK",
    "Pick",
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

  gboolean is_selected;
  g_variant_get_child(result, 0, "b", &is_selected);

  if (is_selected) {
    gchar* result_string;
    g_variant_get_child(result, 1, "s", &result_string);
    printf("%s", result_string); // I would use g_print, but it need a special handler for UTF-8
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

  return is_selected ? 0 : 1;
}
