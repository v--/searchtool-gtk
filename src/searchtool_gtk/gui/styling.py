from gi.repository import Gdk, Gtk


CSS = """
scrolledwindow.scroll-box {
  min-width: 600px;
  min-height: 400px;
}

entry.input {
  min-width: 600px;
  background: none;
  outline: none;
}

label.secondary {
  opacity: 0.5;
}
"""


def apply_styling() -> None:
    style_provider = Gtk.CssProvider()
    style_provider.load_from_string(CSS)

    if display := Gdk.Display.get_default():
        Gtk.StyleContext.add_provider_for_display(
            display,
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
