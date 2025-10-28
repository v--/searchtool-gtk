from gi.repository import Adw, Gio, GObject, Gtk

from ..modes import SearchToolMode
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

        select_prev_action = Gio.SimpleAction(name='select-prev')
        select_prev_action.connect('activate', self.on_select_prev)
        self.add_action(select_prev_action)

        select_next_action = Gio.SimpleAction(name='select-next')
        select_next_action.connect('activate', self.on_select_next)
        self.add_action(select_next_action)

        minimize_action = Gio.SimpleAction(name='minimize')
        minimize_action.connect('activate', self.on_minimize)
        self.add_action(minimize_action)

        submit_action = Gio.SimpleAction(name='submit')
        submit_action.connect('activate', self.on_submit)
        self.add_action(submit_action)

        self.content.refresh_options()

    def on_select_prev(self, action: Gio.Action, parameter: None):
        self.content.select_prev()

    def on_select_next(self, action: Gio.Action, parameter: None):
        self.content.select_next()

    def on_minimize(self, action: Gio.Action, parameter: None):
        self.minimize()
        self.mode.handle_selection_cancellation()

    def on_submit(self, action: Gio.Action, parameter: None):
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
