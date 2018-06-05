import time
import urwid


class TaskPopUp(urwid.WidgetWrap):
    def __init__(self, parent, task):
        self.parent = parent
        self.task = task

        self.lbx_items = self.create_widget_array(
            14,
            [
                ('Node', self.task.node.name),
                ('Type', self.task.type),
                ('Action', self.task.action),
                ('Start time', time.strftime("%Y-%m-%d %H:%M:%S", self.task.start_time)),
                ('Elapsed', "{0:.2f}ms".format(self.task.running_time_ms)),
                ('Cancellable', {True: 'YES', False: 'NO'}[self.task.cancellable]),
                ('Description', self.task.description)
            ]
        )

        self.txt_footer = urwid.Text(
            [
                'Press ',
                ('key', 'Enter'),
                ' to close',
            ]
        )

        self.frm_main = urwid.Frame(
            urwid.AttrWrap(self.lbx_items, 'body'),
            footer=urwid.AttrWrap(self.txt_footer, 'footer')
        )

        self.__super.__init__(urwid.LineBox(self.frm_main, title=self.task.id))

    def create_widget_array(self, title_width, title_values):
        items = []
        for title, value in title_values:
            item = urwid.Columns(
                [
                    (title_width, urwid.Text(('field_title', title + ': '), 'right')),
                    urwid.Text(('field_value', value))
                ]
            )
            items.append(urwid.AttrMap(item, None, 'reveal focus'))

        listbox = urwid.ListBox(urwid.SimpleListWalker(items))

        return listbox

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


class TaskPopUpLauncher(urwid.PopUpLauncher):
    def __init__(self, task):
        self.task = task
        self.__super.__init__(urwid.Text(self.task.id))

    def create_pop_up(self):
        return TaskPopUp(self, self.task)

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 0, 'overlay_width': 76, 'overlay_height': 24}
