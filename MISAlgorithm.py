from CongestGraph import CongestGraph
from GraphVisualization import PrintableGraph
import random


def execute_round(g : CongestGraph):
    message_sent = False
    # send 'active' messages
    for node in g.get_nodes():
        if node.group != 'active':
            continue
        message_sent = True
        for neighbor in node.neighbors:
            g.send_data(node.id, neighbor, False, '{}'.format(node.cluster))
    # read 'active' messages
    for node in g.get_nodes():
        if node.group != 'active':
            continue
        node.messages = []
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id, False)
            if data is not None:
                node.messages.append((int(data), neighbor))
    # do local compute
    for node in g.get_nodes():
        if node.group != 'active':
            continue
        if not node.messages or (node.cluster, node.id) > max(node.messages):
            node.group = 'in'
            node.messages = 'should send no to neighbors'
    # send 'out' messages
    for node in g.get_nodes():
        if node.messages != 'should send no to neighbors':
            continue
        node.messages = None
        for neighbor in node.neighbors:
            g.send_data(node.id, neighbor, False, 'out')
    # read 'out' messages
    for node in g.get_nodes():
        if node.group != 'active':
            continue
        node.messages = None
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id, False)
            if data == 'out':
                node.group = 'out'
                break
    return message_sent

def generate_MIS(g : CongestGraph, c, visualization = False):
    for node in g.get_nodes():
        node.group = 'active'
    upper_limit = len(g.nodes) ** (2 + c)
    message_sent = True
    round_counter = 0
    while message_sent:
        if visualization:
            g.plot(show=False, fps=2)
        for node in g.get_nodes():
            node.cluster = random.randint(0, upper_limit)
        message_sent = execute_round(g)
        round_counter += 1
    if visualization:
        g.plot(show=True)
    return round_counter

def generate_MIS_O_N_determenistic(g : CongestGraph, visualization = False):
    for node in g.get_nodes():
        node.cluster = node.id
        node.group = 'active'
    message_sent = True
    round_counter = 0
    while message_sent:
        if visualization:
            g.plot(show=False, fps=2)
        message_sent = execute_round(g)
        round_counter += 1
    print('finished calculate MIS in {} rounds'.format(round_counter))
    if visualization:
        g.plot(show=True)

def validate_MIS(g : PrintableGraph, visualization = False):
    MIS = []
    for node in g.get_nodes():
        if node.group == 'in':
            MIS.append(node.id)
    ret_val = True
    colored_edges = []
    nodes_colors = {node: 'yellow' for node in MIS}
    nodes = set()
    for u, v in g.edges:
        if u in MIS and v in MIS:
            print('Error - exists edge between node {} to node {} that both in MIS'.format(u, v))
            ret_val = False
            nodes_colors[u] = 'red'
            nodes_colors[v] = 'red'
            colored_edges += [(u, v)]

        if u in MIS or v in MIS:
            nodes.add(u)
            nodes.add(v)
    nodes.update(set(MIS))
    if len(nodes) != len(g.nodes):
        problem_nodes = [node.id for node in g.nodes if node.id not in nodes]
        print('from {} not exists edges to MIS, so MIS isn'"'"'t maximal'.format(problem_nodes))
        ret_val = False
        nodes_colors.update({k: 'purple' for k in problem_nodes})

    if visualization:
        g.plot(nodes_with_colors=nodes_colors, colored_edges=colored_edges)
    return ret_val
