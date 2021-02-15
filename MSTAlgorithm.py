from CongestGraph import CongestGraph
from GraphVisualization import PrintableGraph
import random

# this BFS algorithm run in (2 * tree depth) rounds
# also graph diameter is at least the depth because this is
# the shortest path between the leaf and the root
# also graph diameter is at most the 2 * depth because there is a path
# between each 2 nodes in the tree, and his max length is 2 * depth
def generate_BFS(g : CongestGraph, visualization = False):
    root = random.randint(0, len(g.nodes) - 1)
    g.nodes[root].data['parent'] = [None, True] # parent, first time that parent update
    g.nodes[root].data['sons'] = []
    flag = True
    round_counter = 0
    g.round_start()
    while flag:
        round_counter += 1
        if visualization:
            g.plot(show=False, fps=2)
        for node in g.nodes:
            if 'parent' not in node.data:
                continue
            if node.data['parent'][1] == True:
                node.data['parent'][1] = False
                for neighbor in node.neighbors:
                    if neighbor == node.data['parent'][0]:
                        continue
                    g.send_data(node.id, neighbor, 'parent')
            else:
                node.data['size'] = 1
                for neighbor in node.neighbors:
                    data = g.get_data(neighbor, node.id)
                    if data is not None:
                        data = data.split()
                        if data[0] == 'size:':
                            node.data['size'] += int(data[1])
                            if neighbor not in node.data['sons']:
                                node.data['sons'].append(neighbor)
                            edge = (min(neighbor, node.id), max(neighbor, node.id))
                            g.edges[edge][1] = 'in'
                if node.data['size'] == len(g.nodes):
                    flag = False
        for node in g.nodes:
            if 'parent' in node.data:
                continue
            for neighbor in node.neighbors:
                data = g.get_data(neighbor, node.id)
                if data is not None:
                    data = data.split()
                    if data[0] == 'parent':
                        node.data['parent'] = [neighbor, True]
                        node.data['size'] = 1
                        node.data['sons'] = []
        for node in g.nodes:
            if 'parent' in node.data and node.data['parent'][0] is not None:
                g.send_data(node.id, node.data['parent'][0], 'size: {}'.format(node.data['size']))
    if visualization:
        g.plot(show=True)

def generateMST(g : CongestGraph, visualization = False):
    for edge in g.edges:
        g.edges[edge][1] = 'out'
    g.round_start()
    for _ in range(10):
        for node in g.nodes:
            node.group = node.id
            r = random.randint(0, 1)
            node.data['lead'] = r
        if visualization:
            g.plot(show=False, fps=1, group_to_color=True, follow_lead_to_border=True)
    if visualization:
        g.plot(show=True)

def validateMST(g : CongestGraph):
    w_calculated = 0
    w_real = 0
    for edge in g.edges:
        if g.edges[edge][1] == 'in':
            w_calculated += g.edges[edge][0]
    nodes = ['in'] + (['out'] * (len(g.nodes) - 1))
    while 'out' in nodes:
        min_edge = None
        for (u, v) in g.edges:
            if nodes[u] == nodes[v]:
                continue
            if min_edge is None or g.edges[(u, v)][0] < min_edge[2]:
                min_edge = [u, v, g.edges[(u, v)][0]]
        nodes[min_edge[0]] = 'in'
        nodes[min_edge[1]] = 'in'
        w_real += min_edge[2]
    print(w_real, w_calculated)