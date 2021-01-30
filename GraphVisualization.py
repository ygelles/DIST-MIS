from Graph import Graph
import networkx as nx
from matplotlib import pyplot as plt


class PrintableGraph(Graph):

    def __init__(self):
        super().__init__()

    def plot(self):
        G = nx.Graph()  # this is directed graph
        G.add_edges_from(self.create_edge_list())
        nx.draw(G,  with_labels=True)
        plt.show()

    def plot_and_mark_node_and_edge(self, node, neighbor):
        # https://stackoverflow.com/questions/20133479/how-to-draw-directed-graphs-using-networkx-in-python
        G = nx.Graph()  # this is directed graph
        G.add_edges_from(self.create_edge_list())

        val_map = {node.id: 1.0,
                   neighbor.id: 0.5714285714285714}

        values = [val_map.get(x, 0.25) for x in G.nodes()]

        # Specify the edges you want here
        red_edges = [(node.id, neighbor.id)]

        black_edges = [edge for edge in G.edges() if edge not in red_edges]

        # Need to create a layout when doing
        # separate calls to draw nodes and edges
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),
                               node_color=values, node_size=500)
        nx.draw_networkx_labels(G, pos)
        nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='r')
        nx.draw_networkx_edges(G, pos, edgelist=black_edges)
        plt.show()

    def plot_with_time_color(self, nodes_order=(), fps=3):
        G = nx.Graph()  # this is directed graph
        G.add_edges_from(self.create_edge_list())

        # generate node positions:
        pos = nx.spring_layout(G)

        # draw graph
        nx.draw_networkx(G, pos=pos, font_size=16, node_color='blue', font_color='white')
        plt.pause(1/fps)
        for node in nodes_order:
            # draw subgraph for highlights
            nx.draw_networkx(G.subgraph(node.id), pos=pos, font_size=16, node_color='red', font_color='green')
            plt.pause(1/fps)
        plt.show()

    def create_edge_list(self):
        rows = []
        for i in range(len(self.nodes)):
            cur_node = self.nodes[i]
            for e in cur_node.neighbors:
                rows.append([cur_node.id, e])

        return rows



    # TODO add more methods