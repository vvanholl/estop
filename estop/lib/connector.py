import requests
from threading import Event, Thread

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
        self._timeout = 30
        self._consummed = True
        self._error = None

    def __get_data(self, path=''):
        url = "{0}/{1}".format(self.endpoint, path)

        r = requests.get(url, timeout=self._timeout)
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
        try:
            if 'cluster' in components or 'all' in components:
                self.fetch_cluster_info()
                self.fetch_cluster_health()
            if 'nodes' in components or 'all' in components:
                self.fetch_nodes()
            if 'tasks' in components or 'all' in components:
                self.fetch_tasks()
            self._error = None
        except Exception as e:
            self._error = e
        self._consummed = False

    def get_error(self):
        return self._error

    def is_error(self):
        return True if self._error else False

    def consumme(self):
        if self._consummed:
            return None
        else:
            self._consummed = True
            return self

    def set_timeout(self, timeout):
        self._timeout = timeout


class ConnectorRefreshThread(Thread):
    def __init__(self, connector, refresh_time):
        Thread.__init__(self)
        self.connector = connector
        self._is_paused = False
        self._stopevent = Event()
        self._sleepperiod = refresh_time

    def run(self):
        refresh_count = 0
        while not self._stopevent.isSet():
            if not self._is_paused:
                self.connector.set_timeout(self._sleepperiod)
                if refresh_count % 5 == 0 or self._sleepperiod > 30:
                    self.connector.refresh(['all'])
                else:
                    self.connector.refresh(['tasks'])
                refresh_count = refresh_count + 1
                self._stopevent.wait(self._sleepperiod)

    def join(self, timeout=None):
        self._stopevent.set()
        Thread.join(self, timeout)

    def get_refresh_time(self):
        return self._sleepperiod

    def set_refresh_time(self, refresh_time):
        if refresh_time < 1:
            self._sleepperiod = 1
        elif refresh_time > 60:
            self._sleepperiod = 60
        else:
            self._sleepperiod = refresh_time

    def inc_refresh_time(self):
        self.set_refresh_time(self._sleepperiod + 1)

    def dec_refresh_time(self):
        self.set_refresh_time(self._sleepperiod - 1)

    def is_paused(self):
        return self._is_paused

    def pause(self):
        self._is_paused = not self._is_paused
