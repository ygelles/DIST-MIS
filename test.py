from MISAlgorithm import *

if __name__ == '__main__':
    num_of_iter = 100
    test_types = ['ll', 'st', 'r 3', 'r 5', 'r 7', 'r 10', 'r 20', 'rc 3', 'rc 5', 'rc 7', 'rc 10', 'rc 20']
    with open('output.csv', 'w') as f:
        f.write(','.join(['n'] + test_types))
        f.write('\n')
        for n in [5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]:
            print('start with n: {}, test types: {}, num of iteration: {}'.format(n, len(test_types), num_of_iter))
            f.write(str(n))
            for test_type in test_types:
                res = 0
                for _ in range(num_of_iter):
                    f.write('')
                    g = CongestGraph(100)
                    if test_type == 'll': #linked_list_graph
                        g.create_linked_list_graph(n)
                    elif test_type == 'st': #spanning tree
                        g.create_random_spanning_tree(n)
                    elif test_type.split()[0] == 'r': # random
                        g.create_random_graph(n, min(1, float(test_type.split()[1]) / n))
                    else: # test_type.split()[0] == 'rc': # random connected
                        g.create_random_connected_graph(n, min(1, float(test_type.split()[1]) / n))
                    g.create_buffers()
                    res += generate_MIS(g, 2, False)
                    validate_MIS(g, False)
                f.write(',{}'.format(res/num_of_iter))
            f.write('\n')
