# Distribution MST in CONGEST model

#### In this project we implement distribution MST algorithms with visualization that running in expected run time O(log(|V|) * (diameter + sqrt(|V|)))

### pseudo code:
1. choose BFS root
1. while root subtree size is smaller than |V|:
    1. send a message to all suns
    1. if node haven't parent and get message from another node, set it as parent
    1. read suns subtree size and send it to parent
1. init each node as cluster with same id like the node
1. while there is out edge from the cluster (exists more than 1 cluster):
    1. for each node find local out edge
    1. if cluster size is bigger than sqrt(|V|) send the minimum edge to cluster leader throw the BFS tree, else send it throw the cluster nodes
    1. cluster leader find the global cluster minimum edge and also choose randomly if he is a follower or leader and send it to all cluster nodes (like in 4.ii)
    1. all nodes that is part of cluster minimum edge, and they are also followers notice to the second node in the edge that they are want to merge (and provide there cluster size)
    1. all nodes that they are leader and get the above message forward those message to the cluster leader (like in 4.ii)
    1. the cluster leader calculate the new cluster size and send it (like in 4.ii) to all cluster nodes
    1. the cluster nodes update there size and forward the message to the follower nodes that want to merge
    1. those follower nodes forward the message (like in 4.ii) to cluster leader
    1. the cluster leader send the message (like in 4.ii) to all nodes in cluster
    1. all nodes update there cluster and cluster size

## example with visualization:

### choose the root (node 0)
![BFS stage 0](/images/BFS_0.PNG)

### create the BFS stage #1
![BFS stage 1](/images/BFS_1.PNG)

### create the BFS stage #2
![BFS stage 2](/images/BFS_2.PNG)

### init the clusters
each color represent cluster

border colors:
* green -> leader
* red -> follower
* black -> I don't know yet

![MST stage 0](/images/MST_0.PNG)

### create the MST stage #1
![MST stage 1](/images/MST_1.PNG)

### create the MST stage #2
![MST stage 2](/images/MST_2.PNG)

### create the MST stage #3
![MST stage 3](/images/MST_3.PNG)

### create the MST stage #4
![MST stage 4](/images/MST_4.PNG)

### create the MST stage #5
![MST stage 5](/images/MST_5.PNG)

## execute command

by run main.py it's start interactive shell that support:

Command   | Argument     | Description
--------- | ------------ | -----------
size      | *NUMBER*     | set the size of graph
neighbors | *NUMBER*     | set the expected neighbors in random graph
tree      | ------------ | create a random tree
list      | ------------ | create "snake" graph
random    | ------------ | create random connected graph
MIS       | *True/False* | generate and validate MIS in the graph, the argument is enable the visualization
MST       | *True/False* | generate and validate MST in the graph, the argument is enable the visualization
plot      | ------------ | show the graph
exit      | ------------ | exit from the program

the example in this file can be generated with:
1. size 15
1. neighbor 2
1. random
1. MST True

there are also record of examples in [/images/record.mp4](/images/record.mp4)
