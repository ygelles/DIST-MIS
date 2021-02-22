from MSTAlgorithm import generate_mst, validate_mst
from CongestGraph import CongestGraph

if __name__ == '__main__':
    num_of_iter = 50
    test_types = ['ll', 'st', 'rc 3', 'rc 5', 'rc 7', 'rc 10', 'rc 20']
    for n in [5, 10, 20, 50, 100, 200]:
        print('start with n: {}, test types: {}, num of iteration: {}'.format(n, len(test_types), num_of_iter - (n // 5)))
        for test_type in test_types:
            print('test type:', test_type)
            for i in range(num_of_iter - (n // 5)):
                if (i + 1) % 10 == 0:
                    print('iteration number:', i + 1)
                g = CongestGraph(16, weights=True)
                if test_type == 'll': #linked_list_graph
                    g.create_linked_list_graph(n)
                elif test_type == 'st': #spanning tree
                    g.create_random_spanning_tree(n)
                elif test_type.split()[0] == 'r': # random
                    g.create_random_graph(n, min(1, float(test_type.split()[1]) / n))
                else: # test_type.split()[0] == 'rc': # random connected
                    g.create_random_connected_graph(n, min(1, float(test_type.split()[1]) / n))
                g.create_buffers()
                generate_mst(g, False)
                validate_mst(g, False)

