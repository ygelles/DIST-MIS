from GraphVisualization import PrintableGraph


class Buffer:
    def __init__(self, buffer_size):
        self.__buffer_size = buffer_size
        self.__buffer = []

    def write(self, data):
        raise NotImplementedError()

    def read(self):
        return self.__buffer


class CongestGraph(PrintableGraph):
    def __init__(self):
        super().__init__()
        self.edge_buffers = {} # map edge -> buffer

    def send_message(self, node_from, node_to, msg):
        raise NotImplementedError()