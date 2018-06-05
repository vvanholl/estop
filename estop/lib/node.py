class Node:
    def __init__(self, id, data):
        self.id = id

        self.name = data.get('name')
        self.ip = data.get('ip')
        self.roles = data.get('roles')

        self.cpu_percent = data.get('os').get('cpu').get('percent')
