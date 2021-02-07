from Graph import Graph
from GraphVisualization import PrintableGraph
from CongestGraph import CongestGraph
from MISAlgorithm import *

if __name__ == '__main__':
    g = CongestGraph(100)
    #g.create_random_connected_graph(50, 0)
    g.create_linked_list_graph(50)
    #g.create_graph_from_file('demo_graph.txt')
    g.create_buffers()
    #g.plot()
    #g.create_random_connected_graph(8, 0.2)
    #g.plot_and_mark_node_and_edge(g.nodes[0], g.nodes[2])
    generate_MIS_O_N_determenistic(g, True)
    validate_MIS(g, False)
    #g.plot()
