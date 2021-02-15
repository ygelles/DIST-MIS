import random

WEIGHT_MAX = 5

class InitiationError(Exception):
    pass


class Node:
    def __init__(self, id):
        self.id = id
        self.neighbors = set()
        self.group = 0
        self.data = {}

    def add_neighbor(self, neighbor):
        self.neighbors.add(neighbor)

    def __eq__(self, other):
        return self.id == other.id


class Graph:
    def __init__(self, weights = False):
        self.nodes = []
        self.edges = {}
        self.__initiated = False
        self.weights = weights

    def reset(self):
        self.nodes = []
        self.edges = []
        self.__initiated = False

    def add_node(self, v):
        if v not in self.nodes:
            self.nodes.append(v)

    def add_edge(self, u, v):
        edge = (min(u, v), max(u, v))
        if edge not in self.edges:
            weight = random.randint(1, WEIGHT_MAX) if self.weights else 1
            self.edges[edge] = [weight, 'out']
            self.nodes[u].add_neighbor(v)
            self.nodes[v].add_neighbor(u)

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
            for i, line in enumerate(f):
                self.add_node(Node(i))
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                for neighbor in line.strip().split():
                    self.add_edge(i, int(neighbor))

    def __str__(self):
        return '\n'.join(['Node {} neighbors: {}'.format(node.id, node.neighbors) for node in self.nodes])


if __name__ == '__main__':
     g = Graph()
     g.create_random_graph(8, 0.5)
     #g.create_graph_from_file('demo_graph.txt')
     print(g)