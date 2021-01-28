import random


class InitiationError(Exception):
    pass


class Node:
    def __init__(self, id):
        self.id = id
        self.neighbors = []
        self.group = None
        self.data = None

    def add_neighbor(self, neighbor):
        self.neighbors.append(neighbor)


class Graph:
    def __init__(self):
        self.nodes = []
        self.__initiated = False

    def create_random_graph(self, num_of_nodes, probability_to_edge):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.__initiated = True
        for i in range(num_of_nodes):
            self.nodes.append(Node(i))
        for i in range(num_of_nodes):
            for j in range(num_of_nodes):
                r = random.random()
                if i > j and r < probability_to_edge:
                    self.nodes[i].add_neighbor(j)
                    self.nodes[j].add_neighbor(i)

    def create_graph_from_file(self, filename):
        if self.__initiated:
            raise InitiationError('Graph already initiated')
        self.__initiated = True
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                self.nodes.append(Node(i))
                self.nodes[-1].neighbors = [int(neighbor) for neighbor in line.strip().split()]

    def __str__(self):
        return '\n'.join(['Node {} neighbors: {}'.format(node.id, node.neighbors) for node in self.nodes])


if __name__ == '__main__':
     g = Graph()
     #g.create_random_graph(8, 0.5)
     g.create_graph_from_file('demo_graph.txt')
     print(g)