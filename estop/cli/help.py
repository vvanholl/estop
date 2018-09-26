import urwid


class HelpPopUp(urwid.WidgetWrap):
    def __init__(self, parent):
        self.parent = parent

        help_commands = [
            ('F1 or H', 'Display Help'),
            ('F2', 'Decrease refresh time'),
            ('F3', 'Increase refresh time'),
            ('F4 or P', 'Pause'),
            ('F5 or R', 'Refresh screen'),
            ('F6 or Enter or +/-', 'Fold/Unfold'),
            ('F7 or D', 'Display task detail'),
            ('F8 or C', 'Cancel task'),
            ('F10 or Q', 'Quit program')
        ]

        items = [
            urwid.Padding(urwid.BigText('EsTop', urwid.HalfBlock5x4Font()), width='clip'),
            urwid.Divider('-'),
            urwid.Text('A Task manager for Elasticsearch'),
            urwid.Divider('-'),
        ]

        for key, desc in help_commands:
            item = urwid.Columns(
                [
                    (20, urwid.Text(key)),
                    urwid.Text(desc)
                ]
            )
            items.append(urwid.AttrMap(item, None, 'reveal focus'))

        listbox = urwid.ListBox(urwid.SimpleListWalker(items))

        self.txt_footer = urwid.Text(
            [
                'Press ',
                ('key', 'Enter'),
                ' to close',
            ]
        )

        self.frm_main = urwid.Frame(
            listbox,
            footer=urwid.AttrWrap(self.txt_footer, 'footer')
        )
        self.__super.__init__(urwid.LineBox(self.frm_main, title='Help'))

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


class HelpLauncher(urwid.PopUpLauncher):
    def create_pop_up(self):
        return HelpPopUp(self)

    def open(self):
        self.open_pop_up()

    def get_pop_up_parameters(self):
        return {'left': 5, 'top': 5, 'overlay_width': 60, 'overlay_height': 20}
