from CongestGraph import CongestGraph
from Graph import Node
import random
from math import log2, isqrt

CLUSTER = False
BFS = True
DONT_CARE = CLUSTER




def cluster_is_small(g: CongestGraph, node: Node):
    return node.cluster_size < isqrt(g.size())


# this BFS algorithm run in (2 * tree depth) rounds
# also graph diameter is at least the depth because this is
# the shortest path between the leaf and the root
# also graph diameter is at most the 2 * depth because there is a path
# between each 2 nodes in the tree, and his max length is 2 * depth
# num of rounds is less than 6 * depth
def generate_bfs(g: CongestGraph, visualization=False, fps=0.5):
    start_round = g.rounds
    g.flush_buffers()
    flag = True
    round_counter = 0
    while flag:
        round_counter += 1
        if visualization:
            g.plot(show=False, fps=fps)
        for node in g.get_nodes():
            if node.bfs_parent is None:
                continue
            # first time after node added to the graph, try to add new suns to tree
            if node.bfs_down_queue:
                msg = node.bfs_down_queue[0]
                node.bfs_down_queue = node.bfs_down_queue[1:]
                for neighbor in node.neighbors:
                    if neighbor == node.bfs_parent:
                        continue
                    g.send_data(node.id, neighbor, DONT_CARE, msg)
            # update the subtree size
            else:
                node.sub_tree_size = 1
                for neighbor in node.neighbors:
                    data = g.get_data(neighbor, node.id, DONT_CARE)
                    if data is not None:
                        data = data.split()
                        if data[0] == 'size:':
                            node.sub_tree_size += int(data[1])
                            g.get_edge(neighbor, node.id).status = 'in'
                if node.sub_tree_size == g.size():
                    flag = False
        for node in g.get_nodes():
            if node.bfs_parent is not None:
                continue
            # node without parent receive message and set the parent
            for neighbor in node.neighbors:
                data = g.get_data(neighbor, node.id, DONT_CARE)
                if data is not None:
                    data = data.split()
                    if data[0] == 'parent':
                        node.bfs_parent = neighbor
                        node.bfs_down_queue.append('parent')
                        node.sub_tree_size = 1
        for node in g.get_nodes():
            # send subtree size to parent
            if node.bfs_parent is not None and not node.bfs_root:
                g.send_data(node.id, node.bfs_parent, DONT_CARE, 'size: {}'.format(node.sub_tree_size))
    g.Odiameter = round_counter
    assert g.rounds <= start_round + (g.Odiameter * 3)


# 3 + 4 * sqrt(n) rounds
def generate_bfs_in_cluster(g: CongestGraph):
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        if node.id != node.cluster:
            node.cluster_parent = None
        else:
            node.cluster_down_queue.append('{}'.format(node.cluster))
    for _ in range(2 * isqrt(g.size())):
        for node in g.get_nodes():
            if node.cluster_parent is None or not cluster_is_small(g, node):
                continue
            # first time after node added to the graph, try to add new suns to tree
            if node.cluster_down_queue:
                msg = node.cluster_down_queue[0]
                node.cluster_down_queue = node.cluster_down_queue[1:]
                for neighbor in node.neighbors:
                    if neighbor == node.cluster_parent:
                        continue
                    g.send_data(node.id, neighbor, CLUSTER, msg)
        for node in g.get_nodes():
            if node.cluster_parent is not None or not cluster_is_small(g, node):
                continue
            # node without parent receive message and set the parent
            for neighbor in node.neighbors:
                data = g.get_data(neighbor, node.id, CLUSTER)
                if data is not None:
                    data = data.split()
                    if int(data[0]) == node.cluster:
                        node.cluster_parent = neighbor
                        node.cluster_down_queue.append('{}'.format(node.cluster))
    assert g.rounds <= start_round + 3 + 4 * isqrt(g.size())


# 3 rounds
def find_local_min_edge(g: CongestGraph):
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        node.min_edge = None
    # send node cluster
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            g.send_data(node.id, neighbor, DONT_CARE, '{}'.format(node.cluster))
    # calculate local min edge
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id, DONT_CARE)
            if data is not None and int(data) != node.cluster:
                if node.min_edge is None or g.get_edge(node.id, neighbor).weight < node.min_edge[1]:
                    node.min_edge = (neighbor, g.get_edge(node.id, neighbor).weight)
    assert g.rounds <= start_round + 3


# 1 round
def choose_lead_status(g: CongestGraph):
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        if node.id != node.cluster:
            node.lead = 'IDK'
        else:
            r = random.randint(0, 1)
            node.lead = 'Yes' if r == 1 else 'No'
    assert g.rounds <= start_round + 1


# only cluster root save the messages
# 2 rounds
def send_up_messages_in_cluster(g: CongestGraph):
    start_round = g.rounds
    # read messages from suns
    for node in g.get_nodes():
        if not cluster_is_small(g, node):
            continue
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id, CLUSTER)
            if data is not None:
                if node.id == node.cluster:
                    node.messages.append(data)
                else:
                    node.cluster_up_queue.append(data)
    # send message to parent
    for node in g.get_nodes():
        if not cluster_is_small(g, node):
            continue
        if node.cluster_up_queue:
            msg = node.cluster_up_queue[0]
            del node.cluster_up_queue[0]
            if node.id == node.cluster:
                node.messages.append(msg)
            else:
                g.send_data(node.id, node.cluster_parent, CLUSTER, msg)
    assert g.rounds <= start_round + 2


# all nodes save messages
# 2 rounds
def send_down_messages_in_cluster(g: CongestGraph):
    start_round = g.rounds
    # read message from parent
    for node in g.get_nodes():
        if node.id == node.cluster or not cluster_is_small(g, node):
            continue
        data = g.get_data(node.cluster_parent, node.id, CLUSTER)
        if data is not None:
            node.messages.append(data)
            node.cluster_down_queue.append(data)
    # send messages to suns
    for node in g.get_nodes():
        if not cluster_is_small(g, node):
            continue
        if node.cluster_down_queue:
            msg = node.cluster_down_queue[0]
            del node.cluster_down_queue[0]
            for neighbor in node.neighbors:
                g.send_data(node.id, neighbor, CLUSTER, msg)
    assert g.rounds <= start_round + 2


# only bfs root save the messages
# 2 rounds
def send_up_messages_in_bfs(g: CongestGraph):
    start_round = g.rounds
    # read messages from suns
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id, BFS)
            if data is not None:
                if node.bfs_root:
                    node.bfs_root_messages.append(data)
                else:
                    node.bfs_up_queue.append(data)
    # send message to parent
    for node in g.get_nodes():
        if node.bfs_up_queue:
            msg = node.bfs_up_queue[0]
            del node.bfs_up_queue[0]
            if node.bfs_root:
                node.bfs_root_messages.append(msg)
            else:
                g.send_data(node.id, node.bfs_parent, BFS, msg)
    assert g.rounds <= start_round + 2


# all nodes save messages
# 2 rounds
def send_down_messages_in_bfs(g: CongestGraph):
    start_round = g.rounds
    # read message from parent
    for node in g.get_nodes():
        if node.bfs_root:
            continue
        data = g.get_data(node.bfs_parent, node.id, BFS)
        if data is not None:
            if int(data.split()[1]) == node.cluster:
                node.messages.append(data)
            node.bfs_down_queue.append(data)
    # send messages to suns
    for node in g.get_nodes():
        if node.bfs_down_queue:
            msg = node.bfs_down_queue[0]
            del node.bfs_down_queue[0]
            for neighbor in node.neighbors:
                g.send_data(node.id, neighbor, BFS, msg)
            if int(msg.split()[1]) == node.cluster and node.bfs_root:
                node.messages.append(msg)
    assert g.rounds <= start_round + 2


# 12 * sqrt(n) + 8 * O(diameter)
def send_messages_to_cluster_leader(g: CongestGraph):
    start_round = g.rounds
    # throw cluster
    g.flush_buffers()
    for _ in range(2 * isqrt(g.size())):
        send_up_messages_in_cluster(g)
    g.flush_buffers()

    # throw bfs
    g.flush_buffers()
    for _ in range(4 * (isqrt(g.size()) + g.Odiameter)):
        send_up_messages_in_bfs(g)
    g.flush_buffers()
    assert g.rounds <= start_round + 12 * isqrt(g.size()) + 8 * g.Odiameter


# 12 * sqrt(n) + 8 * O(diameter)
def send_messages_from_cluster_leader(g: CongestGraph):
    start_round = g.rounds
    # throw cluster
    g.flush_buffers()
    for _ in range(2 * isqrt(g.size())):
        send_down_messages_in_cluster(g)
    g.flush_buffers()

    # throw bfs
    g.flush_buffers()
    for _ in range(4 * (isqrt(g.size()) + g.Odiameter)):
        send_down_messages_in_bfs(g)
    g.flush_buffers()
    assert g.rounds <= start_round + 20 * isqrt(g.size()) + 16 * g.Odiameter


def add_message_to_up_queue(g: CongestGraph, node: Node, msg: str):
    if cluster_is_small(g, node):
        if node.id == node.cluster:
            node.messages.append(msg)
        else:
            node.cluster_up_queue.append(msg)
    else:
        if node.bfs_root:
            node.bfs_down_queue.append(msg)
            node.messages.append(msg)
            node.bfs_root_messages.append(msg)
        else:
            node.bfs_up_queue.append(msg)


def add_message_to_down_queue(g: CongestGraph, node: Node, msg: str):
    if cluster_is_small(g, node):
        node.cluster_down_queue.append(msg)
    else:
        if node.bfs_root:
            node.bfs_down_queue.append(msg)
            node.messages.append(msg)
            node.bfs_root_messages.append(msg)
        else:
            node.bfs_up_queue.append(msg)


# 3 + 2 * (12 * sqrt(n) + 8 * O(diameter)) rounds
def share_cluster_min_edge_and_status(g: CongestGraph):
    start_round = g.rounds
    for node in g.get_nodes():
        if node.min_edge is not None:
            add_message_to_up_queue(g, node, 'cluster: {} node: {} min edge: {} lead: {}'.format(node.cluster,
                                                                                                 node.id,
                                                                                                 node.min_edge[1],
                                                                                                 node.lead))
        elif node.cluster == node.id:
            add_message_to_up_queue(g, node, 'cluster: {} node: {} min edge: 9999 lead: {}'.format(node.cluster,
                                                                                                 node.id,
                                                                                                 node.lead))
    send_messages_to_cluster_leader(g)
    # calculate cluster min edge
    for node in g.get_nodes():
        if node.id == node.cluster and cluster_is_small(g,node):
            min_edge = None
            for msg in node.messages:
                _, cluster, _, m_node, _, _, weight, _, _ = msg.split()
                if int(cluster) != node.cluster:
                    continue
                if min_edge is None or int(weight) < min_edge[1]:
                    min_edge = (m_node, int(weight))
            msg = 'cluster: {} status: {} node: {}'.format(node.cluster, node.lead, min_edge[0])
            add_message_to_down_queue(g, node, msg)
            node.messages = [msg]
        else:
            node.messages = []
    root = g.get_root()
    min_edges = {}
    root.status = {}
    for msg in root.bfs_root_messages:
        _, cluster, _, m_node, _, _, weight, _, lead = msg.split()
        if cluster not in min_edges or int(weight) < min_edges[cluster][1]:
            min_edges[cluster] = (m_node, int(weight))
        if lead in ['Yes', 'No']:
            root.status[cluster] = lead
    for cluster in min_edges:
        msg = 'cluster: {} status: {} node: {}'.format(cluster, root.status[cluster], min_edges[cluster][0])
        root.bfs_down_queue.append(msg)
    root.bfs_root_messages = []
    send_messages_from_cluster_leader(g)
    for node in g.get_nodes():
        while node.messages:
            msg = node.messages[0]
            del node.messages[0]
            if msg.find('status') != -1:
                _, cluster, _, status, _, m_node = msg.split()
                if int(cluster) == node.cluster:
                    node.lead = status
                    if int(m_node) != node.id:
                        node.min_edge = None
    assert g.rounds <= start_round + 3 + 2 * (12 * isqrt(g.size()) + 8 * g.Odiameter)


# 7 + 4 * (12 * sqrt(n) + 8 * O(diameter)) rounds
def merge_clusters(g: CongestGraph):
    done = False
    g.clear_nodes_temp_data()
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        if node.min_edge is not None and node.lead == 'No':
            g.send_data(node.id, node.min_edge[0], DONT_CARE,
                        'I want to merge, cluster size: {}'.format(node.cluster_size))
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id, DONT_CARE)
            if data is not None and node.lead == 'Yes':
                cluster_size = data.split()[-1]
                add_message_to_up_queue(g, node, 'cluster: {} cluster size: {}'.format(node.cluster, cluster_size))
    send_messages_to_cluster_leader(g)
    # calculate new cluster size
    for node in g.get_nodes():
        if node.id == node.cluster and node.lead == 'Yes' and cluster_is_small(g, node):
            cluster_size = 0
            for msg in node.messages:
                cluster_size += int(msg.split()[-1])
            add_message_to_down_queue(g, node, 'cluster: {} new cluster size: {}'.format(node.cluster,
                                                                                         cluster_size))
            node.messages = ['cluster: {} new cluster size: {}'.format(node.cluster, cluster_size)]
    root = g.get_root()
    clusters = {}
    for msg in root.bfs_root_messages:
        _, cluster, _, _, cluster_size = msg.split()
        if cluster not in clusters:
            clusters[cluster] = 0
        clusters[cluster] += int(cluster_size)
    for cluster in clusters:
        if root.status[cluster] != 'Yes':
            continue
        msg = 'cluster: {} new cluster size: {}'.format(cluster, clusters[cluster])
        root.bfs_down_queue.append(msg)
    root.bfs_root_messages = []
    send_messages_from_cluster_leader(g)
    for node in g.get_nodes():
        if node.lead != 'Yes':
            continue
        if node.messages:
            node.cluster_size += int(node.messages[-1].split()[-1])
        if node.cluster_size == g.size():
            done = True
        node.messages = []
        for neighbor in node.neighbors:
            g.send_data(node.id, neighbor, DONT_CARE,
                        'cluster leader: {} cluster size: {}'.format(node.cluster, node.cluster_size))
    for node in g.get_nodes():
        if node.min_edge is not None and node.lead == 'No':
            data = g.get_data(node.min_edge[0], node.id, DONT_CARE)
            if data is not None:
                add_message_to_up_queue(g, node, 'cluster: {} {}'.format(node.cluster, data))
                g.get_edge(node.id, node.min_edge[0]).status = 'in'
    send_messages_to_cluster_leader(g)
    for node in g.get_nodes():
        if node.id == node.cluster and node.lead == 'No' and cluster_is_small(g, node):
            msg = None
            while node.messages:
                msg = node.messages[0]
                del node.messages[0]
                if int(msg.split()[1]) == node.cluster and msg.find('cluster leader') != -1:
                    break
            if msg:
                node.messages = [msg]
                add_message_to_down_queue(g, node, msg)
    root = g.get_root()
    clusters = set()
    for msg in root.bfs_root_messages:
        if msg.split()[1] not in clusters:
            clusters.add(msg.split()[1])
            root.bfs_down_queue.append(msg)
    root.bfs_root_messages = []
    send_messages_from_cluster_leader(g)
    for node in g.get_nodes():
        while node.messages:
            msg = node.messages[0]
            del node.messages[0]
            if msg.find('cluster leader') == -1:
                continue
            _, cluster, _, _, new_cluster, _, _, new_size = msg.split()
            if int(cluster) == node.cluster:
                node.cluster = int(new_cluster)
                node.cluster_size = int(new_size)
                node.messages = []
                break
    assert g.rounds <= start_round + 7 + 4 * (12 * isqrt(g.size()) + 8 * g.Odiameter)
    return done


# measured factor is 2.106828418057238
# num of rounds is expected to be less then to (factor)8 * (log2(n)) * (17 + 54 * O(diameter) + 76 * sqrt(n))
def generate_mst(g: CongestGraph, visualization=False, fps=0.5):
    start_round = g.rounds
    g.root = 0  # may randomize
    g.get_node(g.root).bfs_root = True
    g.get_node(g.root).bfs_parent = 'Im (g)root'
    g.get_node(g.root).bfs_down_queue.append('parent')
    generate_bfs(g, visualization=visualization, fps=fps)  # 6 * O(diameter)
    for edge in g.edges:
        g.edges[edge].status = 'out'
    while True:
        g.clear_nodes_temp_data()
        generate_bfs_in_cluster(g)  # 3 + 4 * sqrt(n) rounds
        find_local_min_edge(g)  # 3 rounds
        choose_lead_status(g)  # 1 rounds
        if visualization:
            g.plot(show=False, fps=fps, group_to_color=True, follow_lead_to_border=True)
        share_cluster_min_edge_and_status(g)  # 3 + 2 * (12 * sqrt(n) + 8 * O(diameter)) rounds
        if merge_clusters(g):  # 7 + 4 * (12 * sqrt(n) + 8 * O(diameter)) rounds
            break
        if visualization:
            g.plot(show=False, fps=fps, group_to_color=True, follow_lead_to_border=True)
    if visualization:
        g.plot(show=True, group_to_color=True)
    assert g.rounds <= start_round + 8 * (log2(g.size()) * (17 + 54 * g.Odiameter + 76 * isqrt(g.size())))
    return (g.rounds - start_round) / (log2(g.size()) * (17 + 54 * g.Odiameter + 76 * isqrt(g.size())))


def validate_mst(g: CongestGraph, print_size=True):
    w_calculated = 0
    w_real = 0
    for edge in g.edges:
        if g.edges[edge].status == 'in':
            w_calculated += g.edges[edge].weight
    nodes = ['in'] + (['out'] * (g.size() - 1))
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
    if print_size:
        if w_real == w_calculated:
            print('MST weight {}'.format(w_real))
        else:
            print('MST weight real: {}, calculated: {} ##################################'.format(w_real, w_calculated))
    #assert w_real == w_calculated

