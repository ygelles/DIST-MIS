from Graph import Graph
from GraphVisualization import PrintableGraph
from CongestGraph import CongestGraph
from MSTAlgorithm import *

if __name__ == '__main__':
    graph_size = 33
    expected_neighbors = 2
    g = CongestGraph(30, weights=True)
    g.create_random_connected_graph(graph_size, expected_neighbors / graph_size)
    #g.create_linked_list_graph(10)
    #g.create_graph_from_file('demo_graph_basic.txt')
    #g.create_graph_from_file('demo_graph.txt')
    g.create_buffers()
    #g.plot()
    #g.create_random_connected_graph(8, 0.2)
    #g.plot_and_mark_node_and_edge(g.nodes[0], g.nodes[2])
    #generate_MIS_O_N_determenistic(g, False)
    generate_mst(g, True, fps=2)
    validate_mst(g)
    #generate_MIS(g, 3, True)
    #validate_MIS(g, False)
    #input('press enter:')
    #g.plot(group_to_color=True, follow_lead_to_border=True)
