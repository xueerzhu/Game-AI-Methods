
from math import sqrt
from heapq import heappush, heappop

def dijkstras_shortest_path(src, isdst, adj,subOptimal):
    dist = {}
    prev = {}
    dist[src] = 0
    prev[src] = None
    heap = [(dist[src], src)]

    pathLength = float('inf')
    paths = []
    while heap:
        node = heappop(heap)

        if isdst(node[1]):
            if node[0] < pathLength:
                pathLength = node[0]
                path = []
                nodeR = node[1]
                while nodeR:
                    path.append(nodeR)
                    nodeR = prev[nodeR]
                path.reverse()
                paths.append((node[0],path))
                continue
            elif node[0] > pathLength+subOptimal:
                break
            else:
                path = []
                nodeR = node[1]
                while nodeR:
                    path.append(nodeR)
                    nodeR = prev[nodeR]
                path.reverse()
                paths.append((node[0],path))
                continue

        for next_node in adj(node):
            if next_node[1] not in dist or next_node[0] < dist[next_node[1]]:
                dist[next_node[1]] = next_node[0]
                prev[next_node[1]] = node[1]
                heappush(heap, next_node)

    return paths
