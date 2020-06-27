
from queue import PriorityQueue

from p1_support import load_level, show_level, save_level_costs
from math import inf, sqrt
from heapq import heappop, heappush

def dijkstras_shortest_path(initial_position, destination, graph, adj):
    """ Searches for a minimal cost path through a graph using Dijkstra's algorithm.

    Args:
        initial_position: The initial cell from which the path extends.
        destination: The end location for the path.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        If a path exits, return a list containing all cells from initial_position to destination.
        Otherwise, return None.

    """
    #print('dest ' + str(destination))
    frontier = []
    heappush(frontier, (0, initial_position))  #add initial
    came_from = {}
    cost_so_far = {}
    came_from[initial_position] = None
    cost_so_far[initial_position] = 0

    while len(frontier) is not 0:
        #print('frontier ' + str(list(frontier)))
        current = heappop(frontier)[1] # current node coor

        #print('current ' + str(current))

        if current == destination:

            path = []
            # Path found building it, else return empty path
            node = current
            if node == destination:
                # Go back to the top
                while node is not None:  # while there is a parent (prev[initial_position] = None)
                    path.append(node)
                    node = came_from[node]  # updating to the parent
                # Path is from dst to src, reverse it
                path.reverse()
                print('total cost: {} '.format(cost_so_far[current]))
            return path

        for next_cor in adj(graph, current):
            new_cost = cost_so_far[current] + next_cor[1]
            if next_cor[0] not in cost_so_far or new_cost < cost_so_far[next_cor[0]]:
                cost_so_far[next_cor[0]] = new_cost
                priority = new_cost

                heappush(frontier, (priority, next_cor[0]))

                came_from[next_cor[0]] = current
                #for key, value in came_from.items():
                    #print(key, ' : ', value)

def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """
    pass

    graph_cost = {}
    for cell in graph['spaces'].keys():
        path =dijkstras_shortest_path(initial_position, cell, graph, adj)
        if path:
            #get cost
        else:
            graph_cost[cell] = 'inf'
    for cell in graph['waypoints'].values():
        path =dijkstras_shortest_path(initial_position, cell, graph, adj)
        if path:
            #get cost
        else:
            graph_cost[cell] = 'inf'
    for cell in graph['walls']:
        path =dijkstras_shortest_path(initial_position, cell, graph, adj)
        if path:
            #get cost
        else:
            graph_cost[cell] = 'inf'


def navigation_edges(level, cell):
    """ Provides a list of adjacent cells and their respective costs from the given cell.

    Args:
        level: A loaded level, containing walls, spaces, and waypoints.
        cell: A target location.

    Returns:
        A list of tuples containing an adjacent cell's coordinates and the cost of the edge joining it and the
        originating cell.

        E.g. from (0,0):
            [((0,1), 1),
             ((1,0), 1),
             ((1,1), 1.4142135623730951),
             ... ]
    """
    dirs = [[1, 0],  # basic ones
            [0, 1],
            [-1, 0],
            [0, -1]]
    diag = [[-1, -1],
            [1, -1],
            [-1, 1],
            [1, 1]]
    ogCellCost = 0
    neighborCost = 0

    if cell in level['spaces'].keys():
        ogCellCost = level['spaces'].get(cell)
    if cell in level['waypoints'].values():
        ogCellCost = 1
    if cell in level['walls']:
        ogCellCost = None

    result = []
    for dir in dirs:
        neighbor = (cell[0] + dir[0], cell[1] + dir[1])
        if neighbor in level['spaces']:
            neighborCost = level['spaces'].get(neighbor)
        if neighbor in level['waypoints'].values():
            neighborCost = 1
        if neighbor in level['walls']:
            neighborCost = None
        if neighborCost and ogCellCost is not None:
            neighborEdgeCost = (neighbor, 0.5 * (ogCellCost + neighborCost))
            result.append(neighborEdgeCost)
    for dir in diag:
        neighbor = (cell[0] + dir[0], cell[1] + dir[1])
        if neighbor in level['spaces']:
            neighborCost = level['spaces'].get(neighbor)
        if neighbor in level['waypoints'].values():
            neighborCost = 1
        if neighbor in level['walls']:
            neighborCost = None
        if neighborCost and ogCellCost is not None:
            neighborEdgeCost = (neighbor, 0.5 * sqrt(2) * (ogCellCost + neighborCost))
            result.append(neighborEdgeCost)
    return result


def test_route(filename, src_waypoint, dst_waypoint):
    """ Loads a level, searches for a path between the given waypoints, and displays the result.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        dst_waypoint: The character associated with the destination waypoint.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source and destination coordinates from the level.
    src = level['waypoints'][src_waypoint]
    dst = level['waypoints'][dst_waypoint]

    # Search for and display the path from src to dst.
    path = dijkstras_shortest_path(src, dst, level, navigation_edges)
    if path:
        show_level(level, path)
    else:
        print("No path possible!")


def cost_to_all_cells(filename, src_waypoint, output_filename):
    """ Loads a level, calculates the cost to all reachable cells from 
    src_waypoint, then saves the result in a csv file with name output_filename.

    Args:
        filename: The name of the text file containing the level.
        src_waypoint: The character associated with the initial waypoint.
        output_filename: The filename for the output csv file.

    """

    # Load and display the level.
    level = load_level(filename)
    show_level(level)

    # Retrieve the source coordinates from the level.
    src = level['waypoints'][src_waypoint]

    # Calculate the cost to all reachable cells from src and save to a csv file.
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges(level, src))
    save_level_costs(level, costs_to_all_cells, output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'example.txt', 'a', 'e'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_costs.csv')