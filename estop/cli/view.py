import time
import urwid

class ESTopTaskDetailWidget(urwid.Pile):
	def __init__(self, title_width, titlevalues):
		t = []
		for title, value in titlevalues:
			c = urwid.Columns(
				[
					(title_width, urwid.Text(('field_title', title + ': '), 'right')),
					urwid.Text(('field_value', value))
				]
			)
			t.append(('pack',c))
		self.__super.__init__(t)

class ESTopTaskPopUp(urwid.WidgetWrap):
	def __init__(self, parent, task):
		self.parent = parent
		self.task = task

		self.txt_header = urwid.Text(('title', self.task.id))

		self.pil_body = ESTopTaskDetailWidget(14,
							[
								('Node', self.task.node.name),
								('Type', self.task.type),
								('Action', self.task.action),
								('Description', self.task.description),
								('Start time',time.strftime("%Y-%m-%d %H:%M:%S", self.task.start_time)),
								('Elapsed', "{0:.2f}ms".format(self.task.running_time)),
								('Cancellable', {True: 'YES', False: 'NO'}[self.task.cancellable])
							]
						)

		self.txt_footer = urwid.Text(
			[
				'Go ', ('key', 'B'), 'ack',
				' | ',
				('key', 'C'), 'ancel',
			]
		)

		self.frm_main = urwid.Frame(
			urwid.AttrWrap(self.pil_body, 'body'),
			header=urwid.AttrWrap(self.txt_header, 'head'),
			footer=urwid.AttrWrap(self.txt_footer, 'footer')
		)

		self.__super.__init__(urwid.LineBox(urwid.AttrWrap(self.frm_main, 'title')))

	def keypress(self, size, key):
		key = self.__super.keypress(size, key)
		if key:
			key = self.unhandled_keys(size, key)
		return key

	def unhandled_keys(self, size, key):
		if key in ['b', 'B', 'enter']:
			self.parent.close_pop_up()
		elif key in ['c', 'C']:
			print('cancel')
		else:
			return key

class ESTopTaskPopUpLauncher(urwid.PopUpLauncher):
	def __init__(self, task):
		self.task = task
		self.__super.__init__(urwid.Text(self.task.id))

	def create_pop_up(self):
		return ESTopTaskPopUp(self, self.task)

	def get_pop_up_parameters(self):
		return {'left':0, 'top':0, 'overlay_width':76, 'overlay_height':24}

class ESTopViewTaskWidget(urwid.TreeWidget):
	def __init__(self, node):
		self.task = node.get_value()

		self.__super.__init__(node)

		self._w = urwid.AttrWrap(self._w, None)
		self._w.attr = 'body'
		self._w.focus_attr = 'focus'

		self.expanded_icon = urwid.AttrWrap(self.expanded_icon, None)
		self.expanded_icon.attr = 'body'
		self.expanded_icon.focus_attr = 'focus'

		self.unexpanded_icon = urwid.AttrWrap(self.unexpanded_icon, None)
		self.unexpanded_icon.attr = 'body'
		self.unexpanded_icon.focus_attr = 'focus'

		self.expanded = False

	def get_indented_widget(self):
		self.popup_widget = ESTopTaskPopUpLauncher(self.task)
		indent_cols = self.get_indent_cols()
		return urwid.Columns(
			[
				(42, urwid.Padding(
					urwid.Columns(
						[
							(2, [self.unexpanded_icon, self.expanded_icon][self.expanded]),
							self.popup_widget
						]
					),
					width=('relative', 100), left=indent_cols
				)),
				('weight', 4, urwid.Text(self.task.action)),
				('weight', 3, urwid.Text(self.task.node.name)),
				(20, urwid.Text(time.strftime("%Y-%m-%d %H:%M:%S", self.task.start_time))),
				(14, urwid.Text("{0:8.2f}ms".format(self.task.running_time)))
			]
		)

	def update_expanded_icon(self):
		self._w.base_widget.widget_list[0].original_widget.widget_list[0] = [self.unexpanded_icon, self.expanded_icon][self.expanded]

	def selectable(self):
		return True

	def keypress(self, size, key):
		key = self.__super.keypress(size, key)
		if key:
			key = self.unhandled_keys(size, key)
		return key

	def unhandled_keys(self, size, key):
		if key == "enter":
			self.popup_widget.open_pop_up()
		else:
			return key

class ESTopViewRootWidget(urwid.TreeWidget):
	def __init__(self, node):
		self.__super.__init__(node)

		self._w._original_widget = urwid.Columns(
			[
				(45, urwid.Text(('column_header', 'Task ID'), align='center')),
				('weight', 4, urwid.Text(('column_header', 'Action'), align='center')),
				('weight', 3, urwid.Text(('column_header', 'Node'), align='center')),
				(20, urwid.Text(('column_header', 'Start time'), align='center')),
				(14, urwid.Text(('column_header', 'Elapsed'), align='center'))
			]
		)

class ESTopViewTaskNode(urwid.ParentNode):
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
		return ESTopViewTaskNode(subtask, self, self.depth+1)

	def load_widget(self):
		return ESTopViewTaskWidget(self)

class ESTopViewRootNode(urwid.ParentNode):
	def __init__(self, task, parent=None, depth=0):
		self.depth=depth
		urwid.ParentNode.__init__(self, task, key='/', parent=parent, depth=depth)

	def load_child_keys(self):
		task = self.get_value()
		return [subtask.id for subtask in task.subtasks]

	def load_child_node(self, key):
		task = self.get_value()
		subtask = [subtask for subtask in task.subtasks if subtask.id == key][0]
		return ESTopViewTaskNode(subtask, self, 1)

	def load_widget(self):
		return ESTopViewRootWidget(self)

class ESTopView():
	palette = [
		('body', 'light gray', 'black'),
		('head', 'light gray', 'dark blue'),
		('footer', 'light gray', 'dark blue'),
		('key', 'light cyan', 'dark blue'),
		('title', 'yellow', 'dark blue'),
		('cluster_name', 'white', 'dark blue'),
		('cluster_unknown', 'white', 'black'),
		('cluster_green', 'white', 'dark green'),
		('cluster_yellow', 'white', 'brown'),
		('cluster_red', 'white', 'dark red'),
		('column_header','white','black'),
		('mode_none','white','black'),
		('mode_play','white','dark green'),
		('mode_pause','white','dark red'),
		('focus', 'yellow', 'dark blue'),
		('field_title', 'yellow', 'black'),
		('field_value', 'light gray', 'black'),
	]

	def __init__(self, controller):
		self.controller = controller

		cluster_info = self.controller.poller.get_cluster_info()
		
		self.txt_title = urwid.Text(('title', 'ESTop'))
		self.txt_mode = urwid.Text('', align='center')
		self.map_mode = urwid.AttrMap(self.txt_mode, 'mode_none')
		self.txt_cluster_name = urwid.Text(cluster_info['name'], align='center')
		self.txt_cluster_version = urwid.Text(cluster_info['version'])
		self.txt_cluster_nodes = urwid.Text('')
		self.txt_cluster_status = urwid.Text('', align='center')
		self.map_cluster_status = urwid.AttrMap(self.txt_cluster_status, 'cluster_unknown')
		self.col_header = urwid.Columns(
			[
				(6, self.txt_title),
				(10, self.map_mode),
				self.txt_cluster_name,
				(10, self.txt_cluster_version),
				(10, self.txt_cluster_nodes),
				(10, self.map_cluster_status),
			]
		)

		self.txt_body = urwid.Text('')
		self.fil_body = urwid.Filler(self.txt_body)
		
		self.txt_footer = urwid.Text(
			[
				('key', "P to Play/Pause"),
				' | ',
				('key', "+/- to Fold/Unfold"),
				' | ',
				('key', "Enter for detail"),
				' | ',
				('key', "Q to quit")
			]
		)

		self.frm_main = urwid.Frame(
			urwid.AttrWrap(self.fil_body, 'body'),
			header=urwid.AttrWrap(self.col_header, 'head'),
			footer=urwid.AttrWrap(self.txt_footer, 'footer')
		)

		self.view = self.frm_main

	def refresh(self):
		tasktree = self.controller.poller.get_cluster_tasktree()
		cluster_health = self.controller.poller.get_cluster_health()

		self.txt_cluster_status.set_text(cluster_health['status'])
		self.map_cluster_status.set_attr_map({None:'cluster_' + cluster_health['status']})
		self.txt_cluster_nodes.set_text("{0} nodes".format(cluster_health['number_of_nodes']))
		
		content = urwid.TreeWalker(ESTopViewRootNode(tasktree))
		body = urwid.TreeListBox(content)
		self.frm_main.contents['body'] = (urwid.AttrWrap(body, 'body'), None)

	def set_mode(self, mode):
		if mode == 'play':
			self.txt_mode.set_text('PLAY')
			self.map_mode.set_attr_map({None:'mode_play'})
		else:
			self.txt_mode.set_text('PAUSE')
			self.map_mode.set_attr_map({None:'mode_pause'})

	def unhandled_input(self, k):
		if k == 'p':
			self.controller.play_pause()
		elif k in ('q','Q'):
			raise urwid.ExitMainLoop()
