from Graph import Graph
from GraphVisualization import PrintableGraph
from CongestGraph import CongestGraph
from MSTAlgorithm import *
from MISAlgorithm import *

def interactive_shell():
    graph_size = 10
    expected_neighbors = 2
    g = CongestGraph(30, weights=True)
    while True:
        cmd = input('$ ').split()
        if cmd[0] == 'size':
            graph_size = int(cmd[1])
        if cmd[0] == 'neighbors':
            expected_neighbors = int(cmd[1])
        if cmd[0] == 'list':
            g = CongestGraph(30, weights=True)
            g.create_linked_list_graph(graph_size)
            g.create_buffers()
        if cmd[0] == 'tree':
            g = CongestGraph(30, weights=True)
            g.create_random_spanning_tree(graph_size)
            g.create_buffers()
        if cmd[0] == 'random':
            g = CongestGraph(30, weights=True)
            g.create_random_connected_graph(graph_size, expected_neighbors / graph_size)
            g.create_buffers()
        if cmd[0] == 'MIS':
            generate_MIS(g, 3, bool(cmd[1]))
            validate_MIS(g, False)
        if cmd[0] == 'MST':
            generate_mst(g, bool(cmd[1]), fps=2)
            validate_mst(g, True)
        if cmd[0] == 'plot':
            g.plot()
        if cmd[0] == 'exit':
            break

if __name__ == '__main__':
    interactive_shell()

