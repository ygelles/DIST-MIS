from Graph import Graph
from GraphVisualization import PrintableGraph
from CongestGraph import CongestGraph
from MISAlgorithm import *

if __name__ == '__main__':
    g = PrintableGraph()
    g.create_graph_from_file('demo_graph.txt')
    #g.create_random_connected_graph(8, 0.2)
    #print(g)
    #g.plot_and_mark_node_and_edge(g.nodes[0], g.nodes[2])
    print(validate_MIS(g, [0, 2], visualization=False))
    print(validate_MIS(g, [3, 4, 6, 7]))
    print(validate_MIS(g, [0, 2, 3], visualization=False))
    print(validate_MIS(g, [3, 6, 7], visualization=True))
    print(validate_MIS(g, [0, 3], visualization=True))
    #g.plot_with_time_color(g.nodes)