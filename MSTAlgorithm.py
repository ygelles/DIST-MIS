from CongestGraph import CongestGraph
from GraphVisualization import PrintableGraph
import random


# this BFS algorithm run in (2 * tree depth) rounds
# also graph diameter is at least the depth because this is
# the shortest path between the leaf and the root
# also graph diameter is at most the 2 * depth because there is a path
# between each 2 nodes in the tree, and his max length is 2 * depth
def generate_bfs(g: CongestGraph, visualization=False):
    root = 0
    g.nodes[root].bfs_parent = 'Im root'
    g.nodes[root].bfs_down_queue.append('parent')
    flag = True
    round_counter = 0
    g.round_start()
    while flag:
        round_counter += 1
        if visualization:
            g.plot(show=False, fps=2)
        for node in g.nodes:
            if node.bfs_parent is None:
                continue
            # first time after node added to the graph, try to add new suns to tree
            if node.bfs_down_queue:
                msg = node.bfs_down_queue[0]
                node.bfs_down_queue = node.bfs_down_queue[1:]
                for neighbor in node.neighbors:
                    if neighbor == node.bfs_parent:
                        continue
                    g.send_data(node.id, neighbor, msg)
            # update the subtree size
            else:
                node.data['size'] = 1
                for neighbor in node.neighbors:
                    data = g.get_data(neighbor, node.id)
                    if data is not None:
                        data = data.split()
                        if data[0] == 'size:':
                            node.data['size'] += int(data[1])
                            edge = (min(neighbor, node.id), max(neighbor, node.id))
                            g.edges[edge].status = 'in'
                if node.data['size'] == len(g.nodes):
                    flag = False
        for node in g.nodes:
            if node.bfs_parent is not None:
                continue
            # node without parent receive message and set the parent
            for neighbor in node.neighbors:
                data = g.get_data(neighbor, node.id)
                if data is not None:
                    data = data.split()
                    if data[0] == 'parent':
                        node.bfs_parent = neighbor
                        node.bfs_down_queue.append('parent')
                        node.data['size'] = 1
        for node in g.nodes:
            # send subtree size to parent
            if node.bfs_parent is not None and node.bfs_parent != 'Im root':
                g.send_data(node.id, node.bfs_parent, 'size: {}'.format(node.data['size']))
    if visualization:
        g.plot(show=True)


def generate_mst(g: CongestGraph, visualization=False):
    for edge in g.edges:
        g.edges[edge].status = 'out'
    g.round_start()
    for i in range(10):
        for node in g.nodes:
            if not node.cluster_leader:
                node.lead = 'IDK'
            else:
                r = random.randint(0, 1)
                node.lead = 'Yes' if r == 1 else 'No'
        if visualization:
            g.plot(show=False, fps=1, group_to_color=True, follow_lead_to_border=True)
    if visualization:
        g.plot(show=True)


def validate_mst(g: CongestGraph):
    w_calculated = 0
    w_real = 0
    for edge in g.edges:
        if g.edges[edge].status == 'in':
            w_calculated += g.edges[edge].weight
    nodes = ['in'] + (['out'] * (len(g.nodes) - 1))
    while 'out' in nodes:
        min_edge = None
        for (u, v) in g.edges:
            if nodes[u] == nodes[v]:
                continue
            if min_edge is None or g.edges[(u, v)].weight < min_edge[2]:
                min_edge = [u, v, g.edges[(u, v)].weight]
        nodes[min_edge[0]] = 'in'
        nodes[min_edge[1]] = 'in'
        w_real += min_edge[2]
    print(w_real, w_calculated)