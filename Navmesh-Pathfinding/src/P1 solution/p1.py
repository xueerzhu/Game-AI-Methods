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
    # The priority queue
    queue = [(0, initial_position)]

    # The dictionary that will be returned with the costs
    distances = {}
    distances[initial_position] = 0

    # The dictionary that will store the backpointers
    backpointers = {}
    backpointers[initial_position] = None

    while queue:
        current_dist, current_node = heappop(queue)

        # Check if current node is the destination
        if current_node == destination:

            # List containing all cells from initial_position to destination
            path = [current_node]

            # Go backwards from destination until the source using backpointers
            # and add all the nodes in the shortest path into a list
            current_back_node = backpointers[current_node]
            while current_back_node is not None:
                path.append(current_back_node)
                current_back_node = backpointers[current_back_node]

            return path[::-1]

        # Calculate cost from current note to all the adjacent ones
        for adj_node, adj_node_cost in adj(graph, current_node):
            pathcost = current_dist + adj_node_cost

            # If the cost is new
            if adj_node not in distances or pathcost < distances[adj_node]:
                distances[adj_node] = pathcost
                backpointers[adj_node] = current_node
                heappush(queue, (pathcost, adj_node))

    return None

def dijkstras_shortest_path_to_all(initial_position, graph, adj):
    """ Calculates the minimum cost to every reachable cell in a graph from the initial_position.

    Args:
        initial_position: The initial cell from which the path extends.
        graph: A loaded level, containing walls, spaces, and waypoints.
        adj: An adjacency function returning cells adjacent to a given cell as well as their respective edge costs.

    Returns:
        A dictionary, mapping destination cells to the cost of a path from the initial_position.
    """

    # The priority queue
    queue = [(0, initial_position)]

    # The dictionary that will be returned with the costs
    distances = {}
    distances[initial_position] = 0

    while queue:
        current_dist, current_node = heappop(queue)

        # Calculate cost from current note to all the adjacent ones
        for adj_node, adj_node_cost in adj(graph, current_node):
            pathcost = current_dist + adj_node_cost

            # If the cost is new
            if adj_node not in distances or pathcost < distances[adj_node]:
                distances[adj_node] = pathcost
                heappush(queue, (pathcost, adj_node))

    return distances

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

    adj_cel = {}
    spaces = level['spaces']

    # Visit all adjacent cells
    for delta_x in [-1, 0, 1]:
        for delta_y in [-1, 0, 1]:

            next_cell = (cell[0] + delta_x, cell[1] + delta_y)
            if next_cell != cell and next_cell in spaces.keys():

                # calculate the distance from cell to next_cell
                dist = sqrt(delta_x ** 2 + delta_y ** 2) * 0.5

                # calculate cost and add it to the dict of adjacent cells
                adj_cel[next_cell] = dist * (spaces[cell] + spaces[next_cell])

    return adj_cel.items()


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
    costs_to_all_cells = dijkstras_shortest_path_to_all(src, level, navigation_edges)
    save_level_costs(level, costs_to_all_cells, output_filename)


if __name__ == '__main__':
    filename, src_waypoint, dst_waypoint = 'test_maze.txt', 'a','d'

    # Use this function call to find the route between two waypoints.
    test_route(filename, src_waypoint, dst_waypoint)

    # Use this function to calculate the cost to all reachable cells from an origin point.
    cost_to_all_cells(filename, src_waypoint, 'my_costs.csv')
