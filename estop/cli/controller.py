import urwid

from estop.lib.poller import ESTopPoller
from estop.cli.view import ESTopView


class ESTopController:
    def __init__(self, endpoint):
        self.poller = ESTopPoller(endpoint)
        self.view = ESTopView(self)

        self.view.set_mode('pause')
        self.play_alarm = None

    def main(self):
        self.loop = urwid.MainLoop(self.view.view, self.view.palette,
                                   unhandled_input=self.view.unhandled_input,
                                   pop_ups=True
                                   )
        self.play_pause()
        self.loop.run()

    def play_pause(self):
        if self.play_alarm:
            self.view.set_mode('pause')
            self.loop.remove_alarm(self.play_alarm)
            self.play_alarm = None
        else:
            self.view.set_mode('play')
            self.play_function()

    def play_function(self, loop=None, user_data=None):
        self.view.refresh()
        self.play_alarm = self.loop.set_alarm_in(1, self.play_function)
