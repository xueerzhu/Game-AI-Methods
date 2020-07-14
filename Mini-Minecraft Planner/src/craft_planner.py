import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush

from math import inf

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        items = {}
        try:
            items.update(rule['Consumes'])
        except:
            pass
        try:
            items.update(rule['Requires'])
        except:
            pass
        keys = items.keys()
        for key in keys:
            if state[key] < items[key]:
                return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        state = state.copy()
        try:
            for key in rule['Consumes'].keys():
                state[key] -= rule['Consumes'][key]
        except:
            pass

        for key in rule['Produces'].keys():
            state[key] += rule['Produces'][key]
        
        return state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        
        for g in goal.keys():
            if state[g] < goal[g]:
                return False
        return True
        return state[list(goal.keys())[0]] >= goal[list(goal.keys())[0]]

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)




known_items = {}
def composite(goal, visited_items):
    global known_items
    acc = 0
    for key in goal.keys():
        if key in visited_items:
            return inf
        visited_items.append(key)
        qty = goal[key]
        #what produces this, keep track of time
        sources = []
        lowest_cost = inf
        for r in Crafting['Recipes'].values():
            if key in r['Produces'].keys():
                needed = {}
                needed.update({} if 'Consumes' not in r.keys() else r['Consumes'])
                try:
                    needed.update({k:1 for k in r['Requires'].keys()}) #all required need 1 item
                except:
                    pass

                if len(needed) == 0:
                    return r['Time'] #base case
                
                sub_cost = 0
                if key not in known_items:
                    #known_items[key] = inf #waiting to finish compute
                    cost = composite(needed, visited_items) + r['Time']
                    if cost == inf: #move on, this is already being found, prevent circles
                        continue
                    known_items[key] = cost #dynamic programming 
                    
                    sub_cost = known_items[key] + r['Time'] * (qty/r['Produces'][key])
                elif known_items[key] == inf:
                    continue
                else:
                    sub_cost = known_items[key] + r['Time'] * (qty/r['Produces'][key])

                if lowest_cost > sub_cost:
                    lowest_cost = sub_cost
                #do this if you need to get the recipe.. heappush(itemsNeeded(needed, level + 1 + r['Time'] * (qty/r['Produces'][key]))) #qty/producesCount * time for one + currentLevel
                #sources.append(itemsNeeded(needed, level + 1 + r['Time'] * (qty/r['Produces'][key]))) #qty/producesCount * time for one + currentLevel
        acc += lowest_cost
    return acc

    
    pass

#dict endgoal {"<item>":int}
def heuristic(state, end_goal = None):
    global known_items
    # Implement your heuristic here!
    #return 1
    
    #check if in inventory
    
    #if required, only need one


    known_items = {}
    composite({"ingot":1}, [])


    req = ["furnace",1, "bench",1, "wooden_pickaxe",1, "stone_pickaxe",1, "iron_pickaxe",1, "wooden_axe",0, "stone_axe",0, "iron_axe",0,
            "wood",1, "plank",8, "ore",1, "ingot", 9, "rail", 16, "cart", 1, "coal",1, "cobble", 8, "stick",4]
    for i in state.keys():
        if i not in Crafting['Goal'] and state[i] > req[req.index(i)+1]:
            return inf
    return 0


    


def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    
    #while time() - start_time < limit:
    #    pass

    g = graph(state)
    name, n_state, cost = next(g)

    result = a_star(graph, state, is_goal, limit, heuristic)
    print(time() - start_time, 'seconds.')
    return result

    # # Failed to find a path
    # print(time() - start_time, 'seconds.')
    # print("Failed to find a path from", state, 'within time limit.')
    # return None


def a_star(graph, state, is_goal, limit, heuristic):
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

    frontier = []
    heappush(frontier, (0, state))
    # frontier.put(initial_position, 0)
    came_from = {}
    cost_so_far = {}
    came_from[state] = None
    cost_so_far[state] = 0
    current_state = None
    names = {}
    names[state] = None
    

    while not len(frontier) == 0:
        old_cost, old_state = heappop(frontier)

        # swap
        # temp = current[0]
        # temp1 = current[1]
        
       

        if is_goal(old_state):  # if at waypoint stop
            # came_from[next_pos] = current
            current_state = old_state
            break

        for next in graph(old_state):  # neighbors
            next_name, next_state, next_cost  = next

            new_cost = next_cost + old_cost

            if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                cost_so_far[next_state] = new_cost
                priority = new_cost + heuristic(next_state)
                heappush(frontier, (priority, next_state))
                names[next_state] = next_name
                # frontier.put(next_pos, priority)
                came_from[next_state] = old_state

    # construct path from came_from
    if not is_goal(current_state):
        print("NO PATH FOUND")
        return None

    path = [(current_state,"end")]
    node = current_state
    while node != None:
        path = [(node, names[node])] + path
        node = came_from[node]
    return path


if __name__ == '__main__':
    with open('crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])


    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 30, heuristic)

    # if resulting_plan:
    #     # Print resulting plan
    #     for state, action in resulting_plan:
    #         print('\t',state)
    #         print(action)
