from gi.repository import Gtk, Gdk


CSS = """
label.secondary {
  opacity: 0.5;
}
"""


def apply_styling():
    style_provider = Gtk.CssProvider()
    style_provider.load_from_string(CSS)  # type: ignore[attr-defined]

    if (display := Gdk.Display.get_default()):
        Gtk.StyleContext.add_provider_for_display(
            display,
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
