class ESTopNode:
    def __init__(self, id, data):
        self.id = id
        self.name = data.get('name')
        self.ip = data.get('ip')
