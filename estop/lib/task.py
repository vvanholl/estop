import requests
import time


class RootTask:
    def __init__(self, connector, data):
        self.connector = connector

        self.tasks = {}
        for task_id, task_data in data.items():
            self.tasks[task_id] = Task(self.connector, task_id, task_data)


class Task:
    def __init__(self, connector, id, data):
        self.connector = connector

        self.id = id

        self.node = self.connector.nodes[data.get('node')]
        self.type = data.get('type')
        self.action = data.get('action')
        self.description = data.get('description')

        self.start_time = time.gmtime(float(data.get('start_time_in_millis')) / 1000)
        self.running_time_ms = float(data.get('running_time_in_nanos')) / 1000000

        self.cancellable = data.get('cancellable')

        self.tasks = {}
        for task_data in data.get('children', []):
            task_id = "{0}:{1}".format(task_data.get('node'), task_data.get('id'))
            self.tasks[task_id] = Task(self.connector, task_id, task_data)

    def cancel(self):
        url = "{0}/_tasks/{1}/_cancel".format(self.connector.endpoint, self.id)
        r = requests.post(url, data={})
        if r.status_code != 200:
            raise Exception(
                "Could not cancel task (URL={0}, HTTP code = {1}, Content={2})".format(url, r.status_code, r.text))
