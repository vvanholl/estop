import time


class ESTopRootTask:
	def __init__(self):
		self.subtasks = []

	def add_subtask(self, subtask):
		self.subtasks.append(subtask)

class ESTopTask:
	def __init__(self, id, data, node):
		self.id = id

		self.parent_id = data.get('parent_task_id')
		self.action = data.get('action')
		self.start_time = time.gmtime(float(data.get('start_time_in_millis'))/1000)
		self.running_time = float(data.get('running_time_in_nanos')) / 1000000
		self.description = data.get('description')
		self.cancellable = data.get('cancellable')
		self.type = data.get('type')


		self.node = node

		self.subtasks = []

	def add_subtask(self, subtask):
		self.subtasks.append(subtask)
