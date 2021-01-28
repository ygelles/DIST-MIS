from Graph import Graph


class PrintableGraph(Graph):
    def plot(self):
        raise NotImplementedError()

    def plot_and_mark_node_and_edge(self, node, neighbor):
        raise NotImplementedError()

    # TODO add more methods