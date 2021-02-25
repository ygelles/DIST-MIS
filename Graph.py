import random

WEIGHT_MAX = 5

class InitiationError(Exception):
    pass


class Node:
    def __init__(self, id):
        self.id = id
        self.group = 'active'
        self.neighbors = set()
        self.cluster = id
        self.cluster_size = 1
        self.bfs_parent = None
        self.bfs_root = False
        self.cluster_parent = 'Im (g)root'
        self.lead = None
        self.bfs_up_queue = []
        self.bfs_down_queue = []
        self.cluster_up_queue = []
        self.cluster_down_queue = []
        self.messages = []
        self.sub_tree_size = 1
        self.min_edge = None

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)

    def __eq__(self, other):
        return self.id == other.id

    def __str__(self):
        return 'id: {}\n' \
               'cluster: {}\n' \
               'cluster size: {}\n' \
               'cluster parent: {}\n' \
               'lead: {}\n' \
               'up queue: {}\n' \
               'down queue: {}\n' \
               'bfs messages: {}\n' \
               'neighbors: {}\n' \
               .format(self.id,
                       self.cluster,
                       self.cluster_size,
                       self.cluster_parent,
                       self.lead,
                       self.bfs_up_queue,
                       self.bfs_down_queue,
                       self.messages,
                       self.neighbors)

class Edge:
    def __init__(self, weight):
        self.weight = weight
        self.status = 'out'


class Graph:
    def __init__(self, weights = False):
        self.nodes = []
        self.edges = {}
        self.__initiated = False
        self.weights = weights
        self.rounds = 0
        self.root = None
        self.Odiameter = None

    def add_node(self, v):
        if v not in self.nodes:
            self.nodes.append(v)

    def add_edge(self, u, v, weight=None):
        edge = (min(u, v), max(u, v))
        if edge not in self.edges:
            w = random.randint(1, WEIGHT_MAX) if self.weights else 1
            if weight:
                w = weight
            self.edges[edge] = Edge(w)
            self.nodes[u].add_neighbor(v)
            self.nodes[v].add_neighbor(u)

    def get_edge(self, u, v):
        edge = (min(u, v), max(u, v))
        if edge in self.edges:
            return self.edges[edge]
        return None

    def create_random_graph(self, num_of_nodes, probability_to_edge):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.__initiated = True
        for i in range(num_of_nodes):
            self.add_node(Node(i))
        for i in range(num_of_nodes):
            for j in range(num_of_nodes):
                r = random.random()
                if i > j and r < probability_to_edge:
                    self.add_edge(i, j)

    def create_random_spanning_tree(self, num_of_nodes):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.add_node(Node(0))
        for i in range(1, num_of_nodes):
            self.add_node(Node(i))
            r = random.randint(0, i - 1)
            self.add_edge(i, r)

    def create_random_connected_graph(self, num_of_nodes, probability_to_edge):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.create_random_spanning_tree(num_of_nodes)
        self.__initiated = False
        self.create_random_graph(num_of_nodes, probability_to_edge)

    def create_linked_list_graph(self, num_of_nodes):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.add_node(Node(0))
        for i in range(1, num_of_nodes):
            self.add_node(Node(i))
            self.add_edge(i, i - 1)

    def create_graph_from_file(self, filename):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.__initiated = True
        with open(filename, 'r') as f:
            for i, _ in enumerate(f):
                self.add_node(Node(i))
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                for neighbor in line.strip().split():
                    neighbor, w = neighbor.split(',')
                    self.add_edge(i, int(neighbor), int(w))

    def __str__(self):
        return '\n'.join(['Node {} neighbors: {}'.format(node.id, node.neighbors) for node in self.nodes])

    def debug(self):
        for node in self.nodes:
            print(str(node))

    def clear_nodes_temp_data(self):
        for node in self.nodes:
            node.messages = []
            node.cluster_messages = []
            node.cluster_up_queue = []
            node.cluster_down_queue = []
            node.bfs_up_queue = []
            node.bfs_down_queue = []

    def get_nodes(self):
        self.rounds +=1
        return self.nodes

    def get_node(self, idx):
        return self.nodes[idx]

    def size(self):
        return len(self.nodes)

    def get_root(self):
        return self.nodes[self.root]

if __name__ == '__main__':
     g = Graph()
     g.create_random_graph(8, 0.5)
     #g.create_graph_from_file('demo_graph.txt')
     print(g)