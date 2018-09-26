import urwid


class MessagePopUp(urwid.WidgetWrap):
    def __init__(self, parent, level, message):
        self.parent = parent

        self.txt_message = urwid.Text(message)
        self.fil_message = urwid.Filler(self.txt_message)
        self.txt_footer = urwid.Text(
            [
                'Press ',
                ('key', 'Enter'),
                ' to close',
            ]
        )

        self.frm_main = urwid.Frame(
            urwid.AttrWrap(self.fil_message, "message_{0}".format(level)),
            footer=urwid.AttrWrap(self.txt_footer, 'footer')
        )
        self.__super.__init__(urwid.LineBox(self.frm_main, title=level.capitalize()))

    def keypress(self, size, key):
        key = self.__super.keypress(size, key)
        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        if key == 'enter':
            self.parent.close_pop_up()
        else:
            return key


class MessageLauncher(urwid.PopUpLauncher):
    def __init__(self):
        self.__super.__init__(urwid.Text(' '))
        self.level = 'info'
        self.message = ''

    def create_pop_up(self):
        return MessagePopUp(self, self.level, self.message)

    def open(self, level, message):
        self.level = level
        self.message = message
        self.open_pop_up()

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 0, 'overlay_width': 50, 'overlay_height': 5}
