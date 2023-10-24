from __future__ import annotations
from types import FrameType
from typing import Union
import signal

from setproctitle import setproctitle

from gi.repository import Gio, Adw

from ..config import SearchToolConfigItem
from .content import SearchToolContent


class SearchToolApp(Adw.Application):
    window: Union[Adw.ApplicationWindow, None]
    toolbar: Adw.ToolbarView  # type: ignore
    content: SearchToolContent

    config_list: list[SearchToolConfigItem]

    def __init__(self, config_list: list[SearchToolConfigItem]):
        super().__init__(application_id='net.ivasilev.SearchToolGTK')
        setproctitle('searchtool-gtk')

        for config in config_list:
            signal.signal(signal.SIGRTMIN + config.rt_signal, self.show_window)

        self.config_list = config_list

        self.toolbar = Adw.ToolbarView()  # type: ignore
        self.content = SearchToolContent(self.config_list)

    def run(self, args: list[str] | None):
        exit_status = super().run(args)

        if exit_status > 0:
            raise SystemExit(exit_status)

    def do_activate(self):
        self.window = Adw.ApplicationWindow(application=self, title='SearchTool GTK')
        self.window.set_content(self.toolbar)
        self.content.set_key_capture_widget(self.window)
        self.toolbar.set_content(self.content)

        prev_action = Gio.SimpleAction(name='prev-item')
        prev_action.connect('activate', self.on_prev)
        self.set_accels_for_action('win.prev-item', ['Up'])
        self.window.add_action(prev_action)

        next_action = Gio.SimpleAction(name='next-item')
        next_action.connect('activate', self.on_next)
        self.set_accels_for_action('win.next-item', ['Down'])
        self.window.add_action(next_action)

        minimize_action = Gio.SimpleAction(name='reset_search')
        minimize_action.connect('activate', self.on_minimize)
        self.set_accels_for_action('win.reset_search', ['Escape'])
        self.window.add_action(minimize_action)

        select_action = Gio.SimpleAction(name='select')
        select_action.connect('activate', self.on_select)
        self.set_accels_for_action('win.select', ['Return'])
        self.window.add_action(select_action)

        self.window.present()
        self.content.refresh_options()

        self.window.set_visible(False)

    def on_prev(self, action: Gio.Action, parameter: None):
        self.content.focus_prev()

    def on_next(self, action: Gio.Action, parameter: None):
        self.content.focus_next()

    def on_minimize(self, action: Gio.Action, parameter: None):
        self.content.reset_search()

        if self.window:
            self.window.set_visible(False)

    def on_select(self, action: Gio.Action, parameter: None):
        self.content.select()
        self.content.reset_search()

        if self.window:
            self.window.set_visible(False)

    def show_window(self, sig_num: int, stack_frame: FrameType | None):
        if self.window:
            self.content.set_active(sig_num - signal.SIGRTMIN)
            self.window.set_visible(True)
            self.content.refresh_options()
