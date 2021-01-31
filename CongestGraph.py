from GraphVisualization import PrintableGraph
from math import log2


class Buffer:
    def __init__(self, buffer_size):
        self.__buffer_size = buffer_size
        self.__buffer = None

    def write(self, data):
        if type(data) != str:
            print('its allow to write only string')
            return
        if len(data) > self.__buffer_size:
            print('try to write to much data in CONGEST model')
        else:
            self.__buffer = data

    def read(self):
        data = self.__buffer
        self.__buffer = None
        return data


class CongestGraph(PrintableGraph):
    def __init__(self, alpha):
        super().__init__()
        self.__alpha = alpha
        self.__edge_buffers = {}

    # map edge -> buffer
    def create_buffers(self):
        buffer_size = round(self.__alpha * log2(len(self.nodes)))
        self.__edge_buffers.update({edge: Buffer(buffer_size) for edge in self.edges})
        self.__edge_buffers.update({(edge[1], edge[0]): Buffer(buffer_size) for edge in self.edges})

    def send_data(self, writer, reader, msg):
        edge = (writer, reader)
        if edge not in self.__edge_buffers:
            print('edge not exists')
        else:
            self.__edge_buffers[edge].write(msg)

    def get_data(self, writer, reader):
        edge = (writer, reader)
        if edge not in self.__edge_buffers:
            print('edge not exists')
            return None
        else:
            return self.__edge_buffers[edge].read()

    def get_buffer(self, u, v):
        edge = (min(u, v), max(u, v))
        if edge not in self.__edge_buffers:
            return None
        return self.__edge_buffers[edge]


if __name__ == '__main__':
    g = CongestGraph(1)
    g.create_random_connected_graph(6, 1)
    g.create_buffers()
    g.send_data(0, 1, '1')
    g.send_data(1, 0, '0')
    print(g.get_data(0, 1))
    print(g.get_data(1, 0))
    #g.plot()