from Graph import Graph
import networkx as nx
from matplotlib import pyplot as plt


class PrintableGraph(Graph):

    def __init__(self, weights = False):
        super().__init__(weights)
        self.pos = None
        self.round = None

    def plot(self,
             nodes_with_colors={},
             colored_edges=[],
             show=True,
             fps=3,
             group_to_color=False,
             follow_lead_to_border= False):
        nodes_with_colors = nodes_with_colors.copy()
        colored_edges = colored_edges.copy()
        if not nodes_with_colors and not colored_edges:
            for node in self.nodes:
                if node.group == 'out':
                    nodes_with_colors[node.id] = 'green'
                elif node.group == 'in':
                    nodes_with_colors[node.id] = 'yellow'
                else: # node.group == 'active'
                    nodes_with_colors[node.id] = 'blue'
            for edge in self.edges:
                if self.edges[edge][1] == 'in':
                    colored_edges.append(edge)

        G = nx.Graph()  # this is directed graph
        G.add_weighted_edges_from(self.create_edge_list())

        colors = [nodes_with_colors.get(x, 'green') for x in G.nodes()]
        black_edges = [edge for edge in G.edges() if edge not in colored_edges and (edge[1], edge[0]) not in colored_edges]
        if self.pos is None:
            self.pos = nx.spring_layout(G)
            #mng = plt.get_current_fig_manager()
            #mng.full_screen_toggle()

        if group_to_color:
            colors = [node.group for node in self.nodes]
        borders = None
        linewidth = None
        if follow_lead_to_border:
            borders = ['green' if node.data['lead'] else 'red' for node in self.nodes]
            linewidth = 3
        nx.draw_networkx_nodes(G, self.pos, cmap=plt.get_cmap('jet'),vmin=0,vmax=len(G.nodes)-1,
                               node_color=colors, node_size=500, edgecolors=borders, linewidths=linewidth)
        nx.draw_networkx_labels(G, self.pos, font_color='white')
        nx.draw_networkx_edges(G, self.pos, edgelist=colored_edges, edge_color='r')
        nx.draw_networkx_edges(G, self.pos, edgelist=black_edges)
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=labels)

        if self.round is not None:
            self.round += 1
            plt.title('round number {}'.format(self.round))
        if show:
            plt.show()
        else:
            plt.pause(1/fps)
            plt.clf()

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
        if self.pos is None:
            self.pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, self.pos, cmap=plt.get_cmap('jet'),
                               node_color=values, node_size=500)
        nx.draw_networkx_labels(G, self.pos)
        nx.draw_networkx_edges(G, self.pos, edgelist=red_edges, edge_color='r')
        nx.draw_networkx_edges(G, self.pos, edgelist=black_edges)

        plt.show()

    def plot_with_time_color(self, nodes_order=(), fps=3):
        G = nx.Graph()  # this is directed graph
        G.add_edges_from(self.create_edge_list())

        # generate node positions:
        if self.pos is None:
            self.pos = nx.spring_layout(G)

        # draw graph
        nx.draw_networkx(G, pos=self.pos, font_size=16, node_color='blue', font_color='white')
        plt.pause(1/fps)
        for node in nodes_order:
            # draw subgraph for highlights
            nx.draw_networkx(G.subgraph(node.id), pos=self.pos, font_size=16, node_color='red', font_color='green')
            plt.pause(1/fps)
        plt.show()

    def create_edge_list(self):
        rows = []
        for edge in self.edges:
            rows.append([edge[0], edge[1], self.edges[edge][0]])

        return rows

    def reset(self):
        super().reset()
        self.pos = None
        self.round = None

    def round_start(self):
        self.round = 0


    # TODO add more methods