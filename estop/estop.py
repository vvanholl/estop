#!/usr/bin/env python

import requests
import time
import urwid

class esnode:
	def __init__(self, id, data):
		self.id = id
		self.name = data.get('name')
		self.ip = data.get('ip')

	def __str__(self):
		return "{0}".format(self.name)

class esroottask:
	def __init__(self):
		self.id = ""
		self.subtasks = []

	def add_subtask(self, subtask):
		self.subtasks.append(subtask)

	def __str__(self):
		return "CLUSTER"

class estask:
	def __init__(self, node, id, data):
		self.node = node
		self.id = id
		self.parent_id = data.get('parent_task_id')
		self.action = data.get('action')
		self.start_time = time.gmtime(float(data.get('start_time_in_millis'))/1000)
		self.running_time = float(data.get('running_time_in_nanos')) / 1000000
		self.subtasks = []

	def add_subtask(self, subtask):
		self.subtasks.append(subtask)

	def __str__(self):
		return "{0} {1} {2} {4:.3f}ms".format(self.id, self.node, self.action, time.strftime("%Y-%m-%d %H:%M:%S",self.start_time), self.running_time)

class ESTopModel:
	def __init__(self, endpoint):
		self.endpoint = endpoint

	def get_tasktree(self):
		url = "{0}/_tasks".format(self.endpoint)
		r = requests.get(url)
		if r.status_code == 200:
			data = r.json()
			tasks = {}
			for node_id, node_data in data.get('nodes').items():
				node = esnode(node_id, node_data)
				for task_id, task_data in node_data.get('tasks').items():
					tasks[task_id] = estask(node, task_id, task_data)

			roottask = esroottask()
			for task_id, task in tasks.items():
				if task.parent_id:
					tasks[task.parent_id].add_subtask(task)
				else:
					roottask.add_subtask(task)
			return roottask
		else:
			raise Exception("Could not get tasks from ElasticSearch (http code={0})".format(r.status_code))

class EmptyWidget(urwid.TreeWidget):
	def get_display_text(self):
		return ('flag', '(No task)')

class TaskWidget(urwid.TreeWidget):
	def get_display_text(self):
		node = self.get_node()
		return node.get_value().__str__()

class ESEmptyNode(urwid.TreeNode):
	def load_widget(self):
		return EmptyWidget(self)

class ESTaskNode(urwid.ParentNode):
	def __init__(self, task, parent=None, depth=0):
		self.depth=depth
		key = task.id
		urwid.ParentNode.__init__(self, task, key=key, parent=parent, depth=depth)

	def load_child_keys(self):
		task = self.get_value()
		return [subtask.id for subtask in task.subtasks]

	def load_child_node(self, key):
		task = self.get_value()
		subtask = [subtask for subtask in task.subtasks if subtask.id == key][0]
		return ESTaskNode(subtask, parent=self, depth=self.depth+1)

	def load_widget(self):
		return TaskWidget(self)

class ESTopView:
	palette = [
		('body', 'black', 'light gray'),
		('flagged', 'black', 'dark green', ('bold','underline')),
		('focus', 'light gray', 'dark blue', 'standout'),
		('flagged focus', 'yellow', 'dark cyan',
		('bold','standout','underline')),
		('head', 'yellow', 'black', 'standout'),
		('foot', 'light gray', 'black'),
		('key', 'light cyan', 'black','underline'),
		('title', 'white', 'black', 'bold'),
		('dirmark', 'black', 'dark cyan', 'bold'),
		('flag', 'dark gray', 'light gray'),
		('error', 'dark red', 'light gray'),
		]

	footer_text = [
		('title', "Task browser"), "  ",
		('key', "UP"), ",", ('key', "DOWN"), ",",
		('key', "PAGE UP"), ",", ('key', "PAGE DOWN"),
		"  ",
		('key', "SPACE"), "  ",
		('key', "+"), ",",
		('key', "-"), "  ",
		('key', "LEFT"), "  ",
		('key', "HOME"), "  ",
		('key', "END"), "  ",
		('key', "Q"),
		]

	def __init__(self, endpoint, task):
		self.header = urwid.Text([('title', 'ESTop on '),  endpoint])
		self.body = urwid.TreeListBox(urwid.TreeWalker(ESTaskNode(task)))
		self.footer = urwid.Text(self.footer_text)

		self.frame = urwid.Frame(
			urwid.AttrWrap(self.body, 'body'),
			header=urwid.AttrWrap(self.header, 'head'),
			footer=urwid.AttrWrap(self.footer, 'footer')
		)
		self.view = self.frame

	def main(self):
		self.loop = urwid.MainLoop(self.view, self.palette,
			unhandled_input=self.unhandled_input
		)
		self.loop.run()

	def unhandled_input(self, k):
		if k in ('q','Q'):
			raise urwid.ExitMainLoop()

class ESTopController:
	def __init__(self, endpoint):
		self.endpoint = endpoint
		self.model = ESTopModel(endpoint)

		tasktree = self.model.get_tasktree()
		self.view = ESTopView(endpoint, tasktree)

	def main(self):
		self.view.main()

#ctlr = ESTopController("http://esweb1-production.eu-west-1.csq.io:9200")
ctlr = ESTopController("http://elasticsearch.local.compuscene.net:9200")
ctlr.main()
