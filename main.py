from Graph import Graph
from GraphVisualization import PrintableGraph

if __name__ == '__main__':
    g = PrintableGraph()
    g.create_graph_from_file('demo_graph.txt')
    print(g)
    # g.plot()
    # g.plot_and_mark_node_and_edge(g.nodes[0], g.nodes[2])
    g.plot_with_time_color(g.nodes)