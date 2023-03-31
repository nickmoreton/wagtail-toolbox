class Inspector:
    def __init__(self, host):
        self.host = host
        self.routes = self.get_routes()
