from gi.repository import Adw, Gio, Gtk, GObject

from ..mode import SearchToolMode
from .content import SearchToolContent


class SearchToolWindow(Adw.ApplicationWindow):
    content: SearchToolContent
    mode: SearchToolMode

    def __init__(self, application: Gtk.Application, mode_name: str, mode: SearchToolMode):
        super().__init__(
            application=application,
            title=f'SearchTool GTK: {mode_name}',
            accessible_role=Gtk.AccessibleRole.DIALOG
        )

        self.mode_name = mode_name
        self.mode = mode

        self.content = SearchToolContent(mode_name, mode)
        self.set_content(self.content)
        self.content.set_key_capture_widget(self)

        prev_action = Gio.SimpleAction(name='prev-item')
        prev_action.connect('activate', self.on_prev)
        self.add_action(prev_action)

        next_action = Gio.SimpleAction(name='next-item')
        next_action.connect('activate', self.on_next)
        self.add_action(next_action)

        minimize_action = Gio.SimpleAction(name='reset_search')
        minimize_action.connect('activate', self.on_minimize)
        self.add_action(minimize_action)

        select_action = Gio.SimpleAction(name='select')
        select_action.connect('activate', self.on_select)
        self.add_action(select_action)

        self.content.refresh_options()

    def on_prev(self, action: Gio.Action, parameter: None):
        self.content.select_prev()

    def on_next(self, action: Gio.Action, parameter: None):
        self.content.select_next()

    def on_minimize(self, action: Gio.Action, parameter: None):
        self.minimize()
        self.mode.handle_selection_cancellation()

    def on_select(self, action: Gio.Action, parameter: None):
        selection = self.content.get_selected()
        self.minimize()

        if selection is not None:
            self.mode.bump_item(selection)
            self.mode.activate_item(selection)

        self.emit('submit', selection)

    def minimize(self):
        self.content.reset_search()
        self.set_visible(False)

    def activate(self):
        self.content.refresh_options()
        self.content.reset_search()
        self.set_visible(True)
        self.present()


GObject.signal_new(
    'submit',
    SearchToolWindow,
    0,
    GObject.TYPE_NONE,
    [GObject.TYPE_PYOBJECT]
)
