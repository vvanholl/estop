import urwid

from estop.lib.connector import Connector
from estop.cli.view import View, PALETTE, MODE_PLAY, MODE_PAUSE


class Controller:
    def __init__(self, endpoint, refresh_time):
        self.connector = Connector(endpoint)

        self.set_refresh_time(refresh_time)

        self.view = View(self)

        self.play_alarm = None

        self.loop = urwid.MainLoop(
            self.view.view,
            PALETTE,
            unhandled_input=self.view.unhandled_input,
            pop_ups=True
        )

    def main(self):
        self.play_pause()
        self.loop.run()

    def quit(self):
        raise urwid.ExitMainLoop()

    def play_pause(self):
        if self.play_alarm:
            self.view.set_mode(MODE_PAUSE)
            self.loop.remove_alarm(self.play_alarm)
            self.play_alarm = None
        else:
            self.view.set_mode(MODE_PLAY)
            self.play_function()

    def play_function(self, loop=None, user_data=None):
        self.refresh()
        self.play_alarm = self.loop.set_alarm_in(self.refresh_time, self.play_function)

    def refresh(self):
        self.connector.fetch_cluster_info()
        self.connector.fetch_cluster_health()
        self.connector.fetch_nodes()
        self.connector.fetch_tasks()

        self.view.refresh()

    def set_refresh_time(self, refresh_time):
        if refresh_time < 1:
            refresh_time = 1
        elif refresh_time > 60:
            refresh_time = 60
        self.refresh_time = refresh_time

    def inc_refresh_time(self):
        self.set_refresh_time(self.refresh_time + 1)

    def dec_refresh_time(self):
        self.set_refresh_time(self.refresh_time - 1)
