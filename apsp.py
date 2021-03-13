class Node:
    
    def __init__(self, id: int) -> None:
        # genereal
        self.id: int = id                    # the unique id of the node
        self.graph = None                   # the graph of the node. used for simulation
        self.neighbors: list = []             # the ids of nodes that share an edge with node in graph
        # bfs tree related
        self.root_id: int = self.id          # the id of the node in graph that if the root of the BFS tree
        self.root_dist: int = 0              # the distance between this node to the root node
        self.root_neighbor: int = self.id    # the neighbor that leads to the root node in the BFS tree
        self.leader_messages: list = []       # a queue of messages of type leader (fromNodeId, distToLeader, leaderId)
        self.parent_messages: list = []       # a queue of messages of type parent (childId)
        self.children = []                  # the nodes that route to the leader through this node
        # dfs traverse related
        self.visited = False
        # asps related
        self.wavetimes = dict()
        self.distances = dict()
        self.dist_messages = []

    def send_leader_msg_to(self, u: int):
        assert u in self.neighbors
        assert u in self.graph.nodes
        # simulating message sent
        target: Node = self.graph.get_node(u)
        target.leader_messages.append((self.id, self.root_dist, self.root_id))
    
    def send_parent_msg_to(self, u: int):
        assert u in self.neighbors
        assert u in self.graph.nodes
        target: Node = self.graph.get_node(u)
        target.parent_messages.append(self.id)

    def start_wave(self):
        for uid in self.neighbors:
            self.send_distance_msg_to(uid, self.id)

    def send_distance_msg_to(self, toId: int, ofId: int):
        assert toId in self.neighbors
        assert toId in self.graph.nodes
        target: Node = self.graph.get_node(toId)
        time = self.wavetimes[ofId] if ofId != self.id else 1
        distance = self.distances[ofId][0] if ofId != self.id else 0
        target.dist_messages.append((time, self.id, ofId, distance))


class Graph:

    def __init__(self) -> None:
        self.nodes = dict()
        self.edges = set()
    
    def add_edge(self, v1: int, v2: int):
        assert v1 in self.nodes and v2 in self.nodes and v1 != v2
        edge = (v1, v2)
        self.edges.add((min(edge), max(edge)))

    def add_node(self, node: Node):
        assert node.id not in self.nodes
        self.nodes[node.id] = node
        node.graph = self

    def get_node(self, id: int) -> Node:
        assert id in self.nodes
        return self.nodes[id]

    def __repr__(self) -> str:
        return f"G(V={self.nodes.keys()}, E={self.edges})"

    def printDistances(self):
        print('Distances')
        table = [['from/to'] + [vid for vid in self.nodes]]
        for vid in self.nodes:
            v = self.get_node(vid)
            table += [[vid] + [v.distances[vid] for vid in self.nodes]]
        
        for row in table:
            print(row)

class DFSTraverser:

    def __init__(self, g: Graph) -> None:
        self.graph = g
        self.nodes = [self.graph.get_node(vid) for vid in self.graph.nodes]

    def initialize(self):
        for node in self.nodes:
            node.visited = False
        self.current: Node = self.graph.nodes[min([vid for vid in self.graph.nodes])]

    def get_next_node(self):
        while True:
            if not self.current.visited:
                self.current.visited = True
                return self.current

            for vid in self.current.children:
                child = self.graph.get_node(vid)
                if not child.visited:
                    self.current = child
                    self.current.visited = True
                    return self.current
            
            if self.current.root_neighbor != self.current.id:
                # it is not the root
                self.current = self.graph.get_node(self.current.root_neighbor)
            
            else:
                # every node is visited
                break
        return None

def BFSAlgorithm(g: Graph):
    # Initialize nodes
    for vid in g.nodes:
        v = g.get_node(vid)
        v.root_id = v.id
        v.root_dist = 0
        v.root_neighbor = v.id
        v.graph = g
        v.neighbors = []
        v.parent_messages = []
        v.children = []
    
    for uid, vid in g.edges:
        g.get_node(uid).neighbors.append(vid)
        g.get_node(vid).neighbors.append(uid)
    
    # leader election
    update = True
    while update:
        update = False
        # propagate leaders
        for vid in g.nodes:
            v = g.get_node(vid)
            for u in v.neighbors:
                v.send_leader_msg_to(u)
        
        # update root, parent
        for vid in g.nodes:
            v = g.get_node(vid)
            v.children = []
            while len(v.leader_messages) > 0:
                (fromNodeId, distToLeader, leaderId) = v.leader_messages.pop()
                if (leaderId, distToLeader + 1) < (v.root_id, v.root_dist):
                    # a lower if is found. update.
                    v.root_id = leaderId
                    v.root_dist = distToLeader + 1
                    v.root_neighbor = fromNodeId
                    update = True

        # notify parent
        for vid in g.nodes:
            v = g.get_node(vid)
            if v.root_neighbor != v.id:
                # update parent that you became its children
                v.send_parent_msg_to(v.root_neighbor)
            
        # update children
        for vid in g.nodes:
            v = g.get_node(vid)
            while len(v.parent_messages) > 0:
                childId = v.parent_messages.pop()
                v.children.append(childId)

    return g


def apsp_propagation(g: Graph) -> bool:
    updated = False
    condition = False
    for vid in g.nodes:
        v = g.get_node(vid)
        while len(v.dist_messages) > 0:
            (time, fromId, distOfId, distance) = v.dist_messages.pop()
            condition = False
            if distOfId not in v.wavetimes.keys():
                condition = True
            elif (time + 1, distance + 1) < (v.wavetimes[distOfId], v.distances[distOfId][0]):
                condition = True
            if condition:
                v.distances[distOfId] = (distance + 1, fromId)
                v.wavetimes[distOfId] = time + 1
                updated = True
                print(f"node {v.id} updated dist to {distOfId} = {distance} from {fromId} (time {time})")
        # update neigbors
        if condition:
            for uid in v.neighbors:
                v.send_distance_msg_to(uid, distOfId)

    return updated
            

def APSPAlgorithm(g: Graph):
    # build bfs tree
    g =  BFSAlgorithm(g)

    # initialize the nodes
    for vid in g.nodes:
        v = g.get_node(vid)
        v.visited = False
        v.wavetimes = {v.id: 1}
        v.distances = {v.id: (0, v.id)}
        v.dist_messages = []

    # traverse and wave
    traverser = DFSTraverser(g)
    traverser.initialize()
    updated = True
    round = 0
    while updated:
        updated = False
        v = traverser.get_next_node()
        round += 1
        print("round", round, "DFS")
        if v is not None:
            v.start_wave()
        round += 1
        print("round", round, "propagate")
        updated_1 = apsp_propagation(g)
        round += 1
        print("round", round, "propagate")
        updated_2 = apsp_propagation(g)
        updated = updated_1 or updated_2
    return g
