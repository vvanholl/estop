import urwid

from estop.cli.widget import RootWidget, TaskWidget


class TaskNode(urwid.ParentNode):
    def __init__(self, controller, task, parent, depth):
        self.controller = controller
        urwid.ParentNode.__init__(self, task, key=task.id, parent=parent, depth=depth)

    def load_child_keys(self):
        task = self.get_value()
        return list(task.tasks.keys())

    def load_child_node(self, key):
        task = self.get_value()
        return TaskNode(self.controller, task.tasks[key], self, self.get_depth() + 1)

    def load_widget(self):
        return TaskWidget(self.controller, self)


class RootNode(urwid.ParentNode):
    def __init__(self, controller):
        self.controller = controller
        urwid.ParentNode.__init__(self, controller.connector.task_tree, key='/', parent=None, depth=0)

    def load_child_keys(self):
        task = self.get_value()
        return list(task.tasks.keys())

    def load_child_node(self, key):
        task = self.get_value()
        return TaskNode(self.controller, task.tasks[key], self, 1)

    def load_widget(self):
        return RootWidget(self.controller, self)
