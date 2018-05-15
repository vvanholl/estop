import requests

from estop.lib.node import ESTopNode
from estop.lib.task import ESTopTask, ESTopRootTask


class ESTopPoller:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def get_cluster_data(self, path):
        url = "{0}/{1}".format(self.endpoint, path)

        r = requests.get(url)
        if r.status_code == 200:
            try:
                return r.json()
            except Exception as e:
                raise Exception("Could not decode JSON data from endpoint={0} with path={1}".format(
                    self.endpoint, path))
        else:
            raise Exception("Could not get data from endpoint={0} with path={1} (HTTP code={2})".format(
                self.endpoint, path, r.status_code))

    def get_cluster_info(self):
        data = self.get_cluster_data('')

        try:
            return {
                'name': data.get('cluster_name'),
                'version': data.get('version').get('number')
            }
        except Exception as e:
            raise Exception(
                "Could not fetch cluster info from endpoint={0}".format(self.endpoint))

    def get_cluster_health(self):
        data = self.get_cluster_data('_cluster/health')

        try:
            return {
                'status': data.get('status'),
                'number_of_nodes': data.get('number_of_nodes')
            }
        except Exception as e:
            raise Exception(
                "Could not fetch cluster health from endpoint={0}".format(self.endpoint))

    def get_cluster_tasktree(self):
        data = self.get_cluster_data('_tasks?detailed')
        try:
            tasks = {}
            for node_id, node_data in data.get('nodes').items():
                node = ESTopNode(node_id, node_data)
                for task_id, task_data in node_data.get('tasks').items():
                    tasks[task_id] = ESTopTask(task_id, task_data, node)

            roottask = ESTopRootTask()
            for task_id, task in tasks.items():
                if task.parent_id:
                    if task.parent_id in tasks:
                        tasks[task.parent_id].add_subtask(task)
                else:
                    roottask.add_subtask(task)

            return roottask
        except Exception as e:
            raise Exception(
                "Could not fetch cluster tasks from endpoint={0} ({1})".format(self.endpoint, e))

    def cancel_task(self, task_id):
        url = "{0}/_tasks/{1}/_cancel".format(self.endpoint, task_id)
        print(url)
        r = requests.post(url, data = {})
        if r.status_code == 200:
            print(r.text)
        else:
            raise Exception("Could not cancel task (URL={0}, HTTP code = {1}, Content={2})".format(url, r.status_code, r.text))
