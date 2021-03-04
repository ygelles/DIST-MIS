from apsp import *
from itertools import combinations


def graph_creation_1():
    g = Graph()
    for i in range(2):
        g.add_node(Node(i))
    g.add_edge(0, 1)

    g = BFSAlgorithm(g)
    print(g)
    return g

def graph_creation_2():
    g = Graph()
    for i in range(4):
        g.add_node(Node(i))
    for v1, v2 in combinations(range(4), 2):
        if (v1, v2) in [(0, 3), (3, 0)]:
            continue
        g.add_edge(v1, v2)
    print(g)
    return g

def bfs_and_traverse(g: Graph):
    g = BFSAlgorithm(g)
    print("BFS done")

    traverser = DFSTraverser(g)
    traverser.initialize()
    v = traverser.get_next_node()
    print("beginnig dfs traverse")
    while v is not None:
        print(v.id)
        v = traverser.get_next_node()
    print("traverse ended")
    for vid in g.nodes:
        v = g.get_node(vid)
        assert v.visited

def apsp_test(g: Graph):
    g = APSPAlgorithm(g)
    g.printDistances()
    print("apsp done")

if __name__ == "__main__":
    apsp_test( graph_creation_2() )