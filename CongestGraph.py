from GraphVisualization import PrintableGraph
from math import log2


class Buffer:
    def __init__(self, buffer_size):
        self.__buffer_size = buffer_size
        self.__buffer = None

    def write(self, data):
        if type(data) != str:
            print('its allow to write only string')
            raise ValueError()
        if len(data) > self.__buffer_size:
            print('try to write to much data in CONGEST model')
            raise ValueError()
        else:
            self.__buffer = data

    def read(self):
        data = self.__buffer
        self.__buffer = None
        return data


class CongestGraph(PrintableGraph):
    def __init__(self, alpha, weights = False):
        super().__init__(weights)
        self.__alpha = alpha
        self.__edge_buffers = {}

    # map edge -> buffer
    def create_buffers(self):
        buffer_size = round(self.__alpha * log2(len(self.nodes)))
        for u,v in self.edges:
            for i in [True, False]:
                self.__edge_buffers[(u, v, i)] = Buffer(buffer_size)
                self.__edge_buffers[(v, u, i)] = Buffer(buffer_size)

    def send_data(self, writer, reader, bfs, msg):
        edge = (writer, reader, bfs)
        if edge not in self.__edge_buffers:
            print('edge not exists, writer: {}, reader: {}'.format(writer, reader))
            raise ValueError()
        else:
            self.__edge_buffers[edge].write(msg)

    def get_data(self, writer, reader, bfs):
        edge = (writer, reader, bfs)
        if edge not in self.__edge_buffers:
            print('edge not exists, writer: {}, reader: {}'.format(writer, reader))
            raise ValueError()
        else:
            return self.__edge_buffers[edge].read()

    def reset(self):
        super().reset()
        self.__edge_buffers = {}

    def flush_buffers(self):
        for edge in self.__edge_buffers:
            self.__edge_buffers[edge].read()


if __name__ == '__main__':
    g = CongestGraph(1)
    g.create_random_connected_graph(6, 1)
    g.create_buffers()
    g.send_data(0, 1, '1')
    g.send_data(1, 0, '0')
    print(g.get_data(0, 1))
    print(g.get_data(1, 0))
    #g.plot()