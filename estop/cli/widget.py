import time
import urwid

from estop.cli.popup import TaskPopUpLauncher


class TaskWidget(urwid.TreeWidget):
    def __init__(self, controller, node):
        self.controller = controller
        self.task = node.get_value()

        self.expanded_icon = urwid.AttrWrap(urwid.Text('-'), None)
        self.expanded_icon.attr = 'body'
        self.expanded_icon.focus_attr = 'focus'

        self.unexpanded_icon = urwid.AttrWrap(urwid.Text('+'), None)
        self.unexpanded_icon.attr = 'body'
        self.unexpanded_icon.focus_attr = 'focus'

        self.leaf_icon = urwid.AttrWrap(urwid.Text(' '), None)
        self.leaf_icon.attr = 'body'
        self.leaf_icon.focus_attr = 'focus'

        self.__super.__init__(node)

        self._w = urwid.AttrWrap(self._w, None)
        self._w.attr = 'body'
        self._w.focus_attr = 'focus'

        self.expanded = False

    def get_indented_widget(self):
        self.popup_widget = TaskPopUpLauncher(self.task)
        indent_cols = self.get_indent_cols()

        self.is_branch = True if self.first_child() else False

        if self.is_branch:
            icon = [self.expanded_icon, self.unexpanded_icon][self.expanded]
        else:
            icon = self.leaf_icon

        return urwid.Columns(
            [
                (42, urwid.Padding(
                    urwid.Columns(
                        [
                            (2, icon),
                            self.popup_widget
                        ]
                    ),
                    width=('relative', 100), left=indent_cols
                )),
                ('weight', 4, urwid.Text(self.task.action)),
                ('weight', 3, urwid.Text(self.task.node.name)),
                (20, urwid.Text(time.strftime("%Y-%m-%d %H:%M:%S", self.task.start_time))),
                (14, urwid.Text("{0:8.2f}ms".format(self.task.running_time_ms)))
            ]
        )

    def update_expanded_icon(self):
        self._w.base_widget.widget_list[0].original_widget.widget_list[0] = [
            self.unexpanded_icon, self.expanded_icon][self.expanded]

    def selectable(self):
        return True

    def keypress(self, size, key):
        key = self.__super.keypress(size, key)
        if key:
            key = self.unhandled_keys(size, key)
        return key

    def unhandled_keys(self, size, key):
        if key == 'enter' and self.is_branch:
            self.expanded = not self.expanded
            self.update_expanded_icon()
        elif key in ('d', 'D'):
            self.popup_widget.open_pop_up()
        elif key in ('c', 'C'):
            self.task.cancel()
        else:
            return key


class RootWidget(urwid.TreeWidget):
    def __init__(self, controller, node):
        self.__super.__init__(node)

        self.controller = controller

        self._w._original_widget = urwid.Columns(
            [
                (45, urwid.Text(('column_header', 'Task ID'), align='center')),
                ('weight', 4, urwid.Text(('column_header', 'Action'), align='center')),
                ('weight', 3, urwid.Text(('column_header', 'Node'), align='center')),
                (20, urwid.Text(('column_header', 'Start time'), align='center')),
                (14, urwid.Text(('column_header', 'Elapsed'), align='center'))
            ]
        )
