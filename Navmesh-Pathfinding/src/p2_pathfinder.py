from heapq import heappop, heappushfrom math import inf, sqrtdef find_path(source_point, destination_point, mesh):    """    Searches for a path from source_point to destination_point through the mesh    Args:        source_point: starting point of the pathfinder        destination_point: the ultimate goal the pathfinder must reach        mesh: pathway constraints the path adheres to    Returns:        A path (list of points) from source_point to destination_point if exists        A list of boxes explored by the algorithm    """    point_path = [] #Path to be returned    boxes = [] # NEW: converted to a list    source_box = ()    destination_box = ()    # Identify the source and destination boxes    for box in mesh["boxes"]:        source_point_x = source_point[0]        source_point_y = source_point[1]        if box[0] < source_point_x < box[1] and box[2] < source_point_y < box[3]:            source_box = box        destination_point_x = destination_point[0]        destination_point_y = destination_point[1]        if box[0] < destination_point_x < box[1] and box[2] < destination_point_y < box[3]:            destination_box = box    # Search for and display the path from src to dst.    path = bidirectional_a_star(source_box, destination_box, mesh, destination_point, source_point)    if path:        print("path exists")    else:        print("No path possible!")        return [], [] # return empty lists if no path exists    # handle edge case where source and destination points are inside of the same box    print("path" + str(path))    if source_box == destination_box:        return [source_point, destination_point], [source_box]    else:        prev_point = source_point        path_iter = iter(path)        if source_box is not destination_box:            next(path_iter)  # iterate through first box in path        for box in path:            if box == source_box:                # ADD TWO POINTS TO THE POINT LIST: START POINT AND NEXT POINT			    # ADD ONE BOX TO THE BOX SET: THE STARTING BOX                found_point = find_detail_point(next(path_iter), source_point[0], source_point[1])                point_path.append(source_point)                point_path.append(found_point)                prev_point = found_point                heappush(boxes, source_box)			            elif box == destination_box:                # ADD DESTINATION POINT TO POINT LIST                # ADD DESTINATION BOX TO BOX LIST                point_path.append(destination_point)                heappush(boxes, destination_box)            else:                # ADD ONE POINT TO POINT LIST: THE NEXT POINT FOUND                # ADD ONE BOX TO THE BOX SET: THE CURRENT BOX                print("path_iter: " + str(path_iter))                print("prev_point: " + str(prev_point))                found_point = find_detail_point(next(path_iter), prev_point[0], prev_point[1])                point_path.append(found_point)                print("found_point: " + str(found_point))                heappush(boxes, box)                prev_point = found_point        print("point_path: " + str(point_path))        print("start point: " + str(source_point))        print("end point: " + str(destination_point))        # return a list of points and a list of boxes traversed        return point_path, boxes# Helper function to compute detail point in pathdef find_detail_point(next_box, point_x, point_y):    next_point = ()    next_box_x1 = next_box[0]    next_box_x2 = next_box[1]    next_box_y1 = next_box[2]    next_box_y2 = next_box[3]    # box top right    if point_x <= next_box_x1 and point_y >= next_box_y2:        next_point = (next_box_x1, next_box_y2)    # box top left    elif point_x >= next_box_x2 and point_y >= next_box_y2:        next_point = (next_box_x2, next_box_y2)    # box lower right    elif point_x <= next_box_x1 and point_y <= next_box_y1:        next_point = (next_box_x1, next_box_y1)    # box lower left    elif point_x >= next_box_x2 and point_y <= next_box_y1:        next_point = (next_box_x2, next_box_y1)    # lower box    elif next_box_x1 <= point_x < next_box_x2 and point_y <= next_box_y1:        next_point = (point_x, next_box_y1)    # top box    elif next_box_x1 <= point_x < next_box_x2 and point_y >= next_box_y2:        next_point = (point_x, next_box_y2)    # left box    elif next_box_y1 <= point_y < next_box_y2 and point_x >= next_box_x2:        next_point = (next_box_x2, point_y)    # right box    elif next_box_y1 <= point_y < next_box_y2 and point_x <= next_box_x1:        next_point = (next_box_x1, point_y)    else:        print("empty list")    return next_point# Helpter function to find distance between two pointsdef distance_between_points(point1, point2):    return sqrt(pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2))# bidirectional_a_star implementationdef bidirectional_a_star(initial_box, destination_box, mesh, destination_point, source_point):    """ Searches for a minimal cost path through a graph using bidirectional astar.    Args:        initial_position: init box        destination: dest box        mesh: buildl mesh graph        destination_point: destination point user clicks        source_point: source point user clicks    Returns:        If a path exits, return a list containing all cells from initial_position to destination.        Otherwise, return None.    """    # The priority queue    queue = [(0, initial_box, destination_box)]    heappush(queue,(0, destination_box, initial_box))    # The dictionary that will store the backpointers    backpointers = {}    backpointers[initial_box] = None    # NEW: another dictionary to hold sets of points that build forwards from destination    forwardpointers = {}    forwardpointers[destination_box] = None    #backpointers_back = {}    #backpointers_back[destination_box] = None    cost_table_front = {}    cost_table_back = {}    # NEW: added initial box and destination box to cost tables    cost_table_front[initial_box] = 0    cost_table_back[destination_box] = 0    while queue:        current_dist, current_node, current_goal = heappop(queue)        # return algorithm performs as follows:        """		- current_node should exist in both cost_table_back and cost_table_front...		- therefore, it should also exist in both backpointers and forwardpointers		- start at current_node and build backwards towards the start point, finding one part of the path		- go back to current_node and build forwards towards destination point, finding the rest of the path		- combine both parts of the path and return        """        if (current_node in cost_table_back and current_goal is destination_box) or (current_node in cost_table_front and current_goal is initial_box):            #we are building from front, and have encountered the path building from the back            path = [current_node]            current_back_node = backpointers[current_node]            while current_back_node is not None:                path.append(current_back_node)                current_back_node = backpointers[current_back_node]            # we now have a partial path from current_node back to start            path2 = [current_node]            current_front_node = forwardpointers[current_node]            while current_front_node is not None:                path2.append(current_front_node)                current_front_node = forwardpointers[current_front_node]            # path2 should now have all nodes from current_node to destination in reverse order            path2.remove(current_node)            path2.reverse()            print("path1: " + str(path))            print("path2: " + str(path2))            path2 = path2 + path            return path2[::-1]        if current_goal is destination_box:            for adj_node in mesh["adj"][current_node]:                box_center_point = ((adj_node[0] + adj_node[1]) / 2, (adj_node[2] + adj_node[3]) / 2)                adj_node_cost = distance_between_points(box_center_point, destination_point)                pathcost = current_dist + adj_node_cost                # If the cost is new                # if not in front table                if adj_node not in cost_table_front or pathcost < cost_table_front[adj_node]:                    cost_table_front[adj_node] = pathcost                    backpointers[adj_node] = current_node                    heappush(queue, (pathcost, adj_node, destination_box))        elif current_goal is initial_box:            for adj_node in mesh["adj"][current_node]:                box_center_point = ((adj_node[0] + adj_node[1]) / 2, (adj_node[2] + adj_node[3]) / 2)                adj_node_cost = distance_between_points(box_center_point, source_point)                pathcost = current_dist + adj_node_cost                # If the cost is new                # if not in front table                if adj_node not in cost_table_back or pathcost < cost_table_back[adj_node]:                    cost_table_back[adj_node] = pathcost                    #backpointers[current_node] = adj_node #ISSUE: this will be overwritten for every node adjacent to current node!                    # build a new list of pointers spreading from destination box towards the start box                    forwardpointers[adj_node] = current_node                    heappush(queue, (pathcost, adj_node, initial_box))    return None