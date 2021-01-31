from CongestGraph import CongestGraph
from GraphVisualization import PrintableGraph


def generate_MIS(g : CongestGraph, visualization = False):
    raise NotImplementedError()

def validate_MIS(g : PrintableGraph, MIS : list, visualization = False):
    if visualization:
        raise NotImplementedError()
    nodes = set()
    for u, v in g.edges:
        if u in MIS and v in MIS:
            print('Error - exists edge between node {} to node {} that both in MIS'.format(u, v))
            return False
        if u in MIS or v in MIS:
            nodes.add(u)
            nodes.add(v)
    nodes.update(set(MIS))
    if len(nodes) != len(g.nodes):
        problem_nodes = [node.id for node in g.nodes if node.id not in nodes]
        print('from {} not exists edges to MIS, so MIS isn'"'"'t maximal'.format(problem_nodes))
        return False
    return True