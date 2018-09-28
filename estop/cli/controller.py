import urwid

from estop.lib.connector import Connector, ConnectorRefreshThread
from estop.cli.view import View, PALETTE


class Controller:
    def __init__(self, endpoint, refresh_time):
        self.connector = Connector(endpoint)
        self.connector_refresh_thread = ConnectorRefreshThread(self.connector, refresh_time)

        self.view = View(self)

        self.play_alarm = None

        self.loop = urwid.MainLoop(
            self.view.view,
            PALETTE,
            unhandled_input=self.view.unhandled_input,
            pop_ups=True
        )

    def main(self):
        self.connector_refresh_thread.start()
        self.play_function()
        self.loop.run()

    def quit(self):
        raise urwid.ExitMainLoop()

    def play_function(self, loop=None, user_data=None):
        self.view.refresh()
        self.play_alarm = self.loop.set_alarm_in(0.5, self.play_function)
