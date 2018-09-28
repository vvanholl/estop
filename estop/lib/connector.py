import requests
from threading import Thread
import time

from estop.lib.node import Node
from estop.lib.task import RootTask


class Connector:
    def __init__(self, endpoint):
        self.endpoint = endpoint

        self.cluster_name = ''
        self.cluster_status = 'unknown'
        self.version = ''
        self.number_of_nodes = 0
        self.nodes = {}
        self.task_tree = None
        self.is_consummed = True

    def __get_data(self, path=''):
        url = "{0}/{1}".format(self.endpoint, path)
        r = requests.get(url)

        if r.status_code == 200:
            try:
                return r.json()
            except Exception as e:
                raise Exception("Could not decode JSON data from endpoint={0} with path={1} ({2})".format(
                    self.endpoint, path, e))
        else:
            raise Exception("Could not get data from endpoint={0} with path={1} (HTTP code={2})".format(
                self.endpoint, path, r.status_code))

    def fetch_cluster_info(self):
        data = self.__get_data()
        try:
            self.cluster_name = data.get('cluster_name')
            self.version = data.get('version').get('number')
        except Exception as e:
            raise Exception(
                "Could not fetch cluster info from endpoint={0} ({1})".format(self.endpoint, e))

    def fetch_cluster_health(self):
        data = self.__get_data('_cluster/health')
        try:
            self.cluster_status = data.get('status')
            self.number_of_nodes = data.get('number_of_nodes')
        except Exception as e:
            raise Exception(
                "Could not fetch cluster health from endpoint={0} ({1})".format(self.endpoint, e))

    def fetch_nodes(self):
        data = self.__get_data('_nodes/stats')
        self.nodes = {}
        for node_id, node_data in data.get('nodes').items():
            self.nodes[node_id] = Node(node_id, node_data)

    def fetch_tasks(self):
        data = self.__get_data('_tasks?group_by=parents&detailed')
        try:
            self.task_tree = RootTask(self, data.get('tasks'))
        except Exception as e:
            raise Exception("Could not fetch cluster tasks from endpoint={0} ({1})".format(self.endpoint, e))

    def refresh(self, components):
        if 'cluster' in components or 'all' in components:
            self.fetch_cluster_info()
            self.fetch_cluster_health()

        if 'nodes' in components or 'all' in components:
            self.fetch_nodes()

        if 'tasks' in components or 'all' in components:
            self.fetch_tasks()

        self.is_consummed = False

    def consumme(self):
        if self.is_consummed:
            return None
        else:
            self.is_consummed = True
            return self


class ConnectorRefreshThread(Thread):
    def __init__(self, connector, refresh_time):
        Thread.__init__(self)
        self.connector = connector
        self.refresh_time = refresh_time
        self.is_paused = False

    def run(self):
        refresh_count = 0
        while True:
            if not self.is_paused:
                if refresh_count % 5 == 0 or self.refresh_time > 30:
                    self.connector.refresh(['all'])
                else:
                    self.connector.refresh(['tasks'])
                refresh_count = refresh_count + 1
                time.sleep(self.refresh_time)

    def set_refresh_time(self, refresh_time):
        if refresh_time < 1:
            self.refresh_time = 1
        elif refresh_time > 60:
            self.refresh_time = 60
        else:
            self.refresh_time = refresh_time

    def inc_refresh_time(self):
        self.set_refresh_time(self.refresh_time + 1)

    def dec_refresh_time(self):
        self.set_refresh_time(self.refresh_time - 1)

    def pause(self):
        self.is_paused = not self.is_paused
