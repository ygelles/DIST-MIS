from CongestGraph import CongestGraph
from GraphVisualization import PrintableGraph
import random
from math import log2


# this BFS algorithm run in (2 * tree depth) rounds
# also graph diameter is at least the depth because this is
# the shortest path between the leaf and the root
# also graph diameter is at most the 2 * depth because there is a path
# between each 2 nodes in the tree, and his max length is 2 * depth
# num of rounds is less than 3 * 2 * depth
def generate_bfs(g: CongestGraph, visualization=False):
    start_round = g.rounds
    g.flush_buffers()
    flag = True
    round_counter = 0
    while flag:
        round_counter += 1
        if visualization:
            g.plot(show=False, fps=2)
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
                    g.send_data(node.id, neighbor, msg)
            # update the subtree size
            else:
                node.sub_tree_size = 1
                for neighbor in node.neighbors:
                    data = g.get_data(neighbor, node.id)
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
                data = g.get_data(neighbor, node.id)
                if data is not None:
                    data = data.split()
                    if data[0] == 'parent':
                        node.bfs_parent = neighbor
                        node.bfs_down_queue.append('parent')
                        node.sub_tree_size = 1
        for node in g.get_nodes():
            # send subtree size to parent
            if node.bfs_parent is not None and not node.bfs_root:
                g.send_data(node.id, node.bfs_parent, 'size: {}'.format(node.sub_tree_size))
    depth = (round_counter // 2) + 1
    assert g.rounds <= start_round + (depth * 2 * 3)
    return depth


# num of rounds is equal to 1 + (n * 2) should be 1 + (constant * sqrt(n))
def generate_bfs_in_cluster(g: CongestGraph):
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        if node.id != node.cluster:
            node.cluster_parent = None
        else:
            node.cluster_down_queue.append('{}'.format(node.cluster))
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        for node in g.get_nodes():
            if node.cluster_parent is None:
                continue
            # first time after node added to the graph, try to add new suns to tree
            if node.cluster_down_queue:
                msg = node.cluster_down_queue[0]
                node.cluster_down_queue = node.cluster_down_queue[1:]
                for neighbor in node.neighbors:
                    if neighbor == node.cluster_parent:
                        continue
                    g.send_data(node.id, neighbor, msg)
        for node in g.get_nodes():
            if node.cluster_parent is not None:
                continue
            # node without parent receive message and set the parent
            for neighbor in node.neighbors:
                data = g.get_data(neighbor, node.id)
                if data is not None:
                    data = data.split()
                    if int(data[0]) == node.cluster:
                        node.cluster_parent = neighbor
                        node.cluster_down_queue.append('{}'.format(node.cluster))
    assert g.rounds <= start_round + 1 + (g.size() * 2)


# num of rounds is equal to 3 rounds
def find_local_min_edge(g: CongestGraph):
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        node.min_edge = None
    # send node cluster
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            g.send_data(node.id, neighbor, '{}'.format(node.cluster))
    # calculate local min edge
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id)
            if data is not None and int(data) != node.cluster:
                if node.min_edge is None or g.get_edge(node.id, neighbor).weight < node.min_edge[1]:
                    node.min_edge = (neighbor, g.get_edge(node.id, neighbor).weight)
    assert g.rounds <= start_round + 3


# num of rounds is equal to 1 round
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
# num of rounds is equal to 2 rounds
def send_up_messages_in_cluster(g: CongestGraph):
    start_round = g.rounds
    # read messages from suns
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id)
            if data is not None:
                if node.id == node.cluster:
                    node.messages.append(data)
                else:
                    node.cluster_up_queue.append(data)
    # send message to parent
    for node in g.get_nodes():
        if node.cluster_up_queue:
            msg = node.cluster_up_queue[0]
            del node.cluster_up_queue[0]
            if node.id == node.cluster:
                node.messages.append(msg)
            else:
                g.send_data(node.id, node.cluster_parent, msg)
    assert g.rounds <= start_round + 2


# all nodes save messages
# num of rounds is equal to 2 rounds
def send_down_messages_in_cluster(g: CongestGraph):
    start_round = g.rounds
    # read message from parent
    for node in g.get_nodes():
        if node.id == node.cluster:
            continue
        data = g.get_data(node.cluster_parent, node.id)
        if data is not None:
            node.messages.append(data)
            node.cluster_down_queue.append(data)
    # send messages to suns
    for node in g.get_nodes():
        if node.cluster_down_queue:
            msg = node.cluster_down_queue[0]
            del node.cluster_down_queue[0]
            for neighbor in node.neighbors:
                g.send_data(node.id, neighbor, msg)
    assert g.rounds <= start_round + 2


# num of rounds is equal to 3 + (4 * n) rounds should be 1 + (constant * sqrt(n) + diameter)
def share_cluster_min_edge_and_status(g: CongestGraph):
    start_round = g.rounds
    for node in g.get_nodes():
        if node.min_edge is not None:
            node.cluster_up_queue.append('node: {} min edge: {}'.format(node.id, node.min_edge[1]))
    g.flush_buffers()
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        send_up_messages_in_cluster(g)
    g.flush_buffers()
    # calculate cluster min edge
    for node in g.get_nodes():
        if node.id == node.cluster:
            min_edge = None
            for msg in node.messages:
                _, m_node, _, _, weight = msg.split()
                if min_edge is None or int(weight) < min_edge[1]:
                    min_edge = (m_node, int(weight))
            if min_edge is None:
                assert g.rounds <= start_round + 3 + (4 * g.size())
                return True
            node.cluster_down_queue.append('status: {} node: {}'.format(node.lead, min_edge[0]))
            node.messages = [node.cluster_down_queue[-1]]
    g.flush_buffers()
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        send_down_messages_in_cluster(g)
    g.flush_buffers()
    for node in g.get_nodes():
        _, status, _, m_node = node.messages[0].split()
        del node.messages[0]
        node.lead = status
        if int(m_node) != node.id:
            node.min_edge = None
    assert g.rounds <= start_round + 3 + (4 * g.size())
    return False


# num of rounds is equal to 7 + (8 * n) rounds should be 1 + (constant * sqrt(n) + diameter)
def merge_clusters(g: CongestGraph):
    start_round = g.rounds
    g.flush_buffers()
    for node in g.get_nodes():
        if node.min_edge is not None and node.lead == 'No':
            g.send_data(node.id, node.min_edge[0], 'I want to merge, cluster size: {}'.format(node.cluster_size))
    for node in g.get_nodes():
        for neighbor in node.neighbors:
            data = g.get_data(neighbor, node.id)
            if data is not None and node.lead == 'Yes':
                cluster_size = data.split()[-1]
                node.cluster_up_queue.append('cluster size: {}'.format(cluster_size))
    g.flush_buffers()
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        send_up_messages_in_cluster(g)
    g.flush_buffers()
    # calculate new cluster size
    for node in g.get_nodes():
        if node.id == node.cluster and node.lead == 'Yes':
            for msg in node.messages:
                node.cluster_size += int(msg.split()[-1])
            node.cluster_down_queue.append('new cluster size: {}'.format(node.cluster_size))
            node.messages = [node.cluster_down_queue[-1]]
    g.flush_buffers()
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        send_down_messages_in_cluster(g)
    g.flush_buffers()
    for node in g.get_nodes():
        if node.lead == 'No':
            continue
        node.cluster_size = int(node.messages[0].split()[-1])
        del node.messages[0]
        for neighbor in node.neighbors:
            g.send_data(node.id, neighbor, 'cluster leader: {} cluster size: {}'.format(node.cluster, node.cluster_size))
    for node in g.get_nodes():
        if node.min_edge is not None and node.lead == 'No':
            data = g.get_data(node.min_edge[0], node.id)
            if data is not None:
                node.cluster_up_queue.append(data)
                g.get_edge(node.id, node.min_edge[0]).status = 'in'
    g.flush_buffers()
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        send_up_messages_in_cluster(g)
    g.flush_buffers()
    for node in g.get_nodes():
        if node.id == node.cluster and node.lead == 'No' and node.messages:
            msg = node.messages[0]
            node.cluster_down_queue.append(msg)
            node.messages = [node.cluster_down_queue[-1]]
    g.flush_buffers()
    for _ in range(g.size()):  # TODO should change to sqrt g.nodes
        send_down_messages_in_cluster(g)
    g.flush_buffers()
    for node in g.get_nodes():
        if node.messages:
            _, _, new_cluster, _, _, new_size = node.messages[0].split()
            del node.messages[0]
            node.cluster = int(new_cluster)
            node.cluster_size = int(new_size)
    assert g.rounds <= start_round + 7 + (8 * g.size())


# num of rounds is expected to be less then to 8 * (log2(n)) * ((3 * 2 * depth) + 15 + (14 * n)) should replace the last n with sqrt(n)
def generate_mst(g: CongestGraph, visualization=False, fps=6):
    start_round = g.rounds
    root = 0  # may randomize
    g.get_node(root).bfs_root = True
    g.get_node(root).bfs_parent = 'Im (g)root'
    g.get_node(root).bfs_down_queue.append('parent')
    depth = generate_bfs(g, visualization=visualization)  # 3 * 2 * depth
    for edge in g.edges:
        g.edges[edge].status = 'out'
    while True:
        g.clear_nodes_temp_data()
        generate_bfs_in_cluster(g)  # num of rounds is equal to 1 + (n * 2)
        find_local_min_edge(g)  # num of rounds is equal to 3 rounds
        choose_lead_status(g)  # num of rounds is equal to 1 rounds
        if visualization:
            g.plot(show=False, fps=fps, group_to_color=True, follow_lead_to_border=True)
        if share_cluster_min_edge_and_status(g):  # num of rounds is equal to 3 + (4 * n) rounds
            break
        if visualization:
            g.plot(show=False, fps=fps, group_to_color=True, follow_lead_to_border=True)
        merge_clusters(g)
    if visualization:
        g.plot(show=True, group_to_color=True)  # num of rounds is equal to 7 + (8 * n) rounds
    assert g.rounds <= start_round + 2 * 8 * round(log2(g.size())) * ((3 * 2 * depth) + 15 + (14 * g.size()))


def validate_mst(g: CongestGraph):
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
    assert w_real == w_calculated
    print('MST weight: {}'.format(w_real))
