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


def make_checker_regression(rule):
    # Goal regression backwards search
    # requires and produces fields are true in the current state

    def check_regression(state):
        objects = {}
        try:
            objects.update(rule['Produces'])
        except:
            pass
        try:
            objects.update(rule['Requires'])
        except:
            pass

        for key, value in objects.items():
            if state.get(key) <= 0:  #if I have this item
                return False
        return True

        # for key, value in objects.items():
        #     if state.get(key) > 0:  #if I have this item
        #         return True
        # return False


    return check_regression


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


def make_effector_regression(rule):
    # Goal regression backwards search
    # Can the current state produces the goal rule
    # - produced items;  + consumed items

    def effect_regression(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        state = state.copy()
        try:
            for key in rule['Consumes'].keys():
                state[key] += rule['Consumes'][key]
        except:
            pass

        for key in rule['Produces'].keys():
            state[key] -= rule['Produces'][key]

        # # if we don't have the required item, we add it to consumes list, but we don't need more than 1
        # try:
        #     require_object = list(rule.get('Requires'))[0]
        #     if state.get(require_object) <= 0:
        #         # we get required
        #         state[require_object] = 1
        # except:
        #     pass
        return state

    return effect_regression


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        return state[list(goal.keys())[0]] >= goal[list(goal.keys())[0]]

    return is_goal


def make_goal_checker_regression(initial):
    # Goal regression backwards search
    # requires and produces fields are true in the current state

    def is_goal_regression(state):
        for key in initial.keys():
            if state[key] <= initial[key]:
                return True
        return False

    return is_goal_regression


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.

    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def graph_regression(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.

    # can we find a recipe that has all the produce and require
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)



# dict endgoal {"<item>":int}
def heuristic(state, end_goal=None):
    # Implement your heuristic here!
    # return 1

    # check if in inventory

    # if required, only need one

    req = ["furnace", 1, "bench", 1, "wooden_pickaxe", 1, "stone_pickaxe", 1, "iron_pickaxe", 1, "wooden_axe", 1,
           "stone_axe", 1, "iron_axe", 1,
           "wood", 1, "plank", 8, "ore", 1, "ingot", 9, "rail", 16, "cart", 1, "coal", 1, "cobble", 8, "stick", 4]
    for i in state.keys():
        if i not in Crafting['Goal'] and state[i] > req[req.index(i) + 1]:
            return inf
    return 0

    # check cost

    items_total = 0
    for key in end_goal.keys():
        if end_goal[key] - state[key] > 0:
            items_total += end_goal[key] - state[key]
    return items_total
    # return 1 if state[goal] > 0 else 0


def search(graph, state, is_goal, limit, heuristic):
    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state

    #while time() - start_time < limit:
       #pass

    g = graph(state)
    name, n_state, cost = next(g)

    return a_star(graph, state, is_goal, limit, heuristic)

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
            next_name, next_state, next_cost = next

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

    path = [(current_state, "end")]
    node = current_state
    while node != None:
        path = [(node, names[node])] + path
        node = came_from[node]
    return path

def check_requiremnt(rule):
    def requirment(state):
        # Returns a state if requirment object is missing
        # returns unaltered state if not
        # are we missing a requirement
        have_recipe = 0
        for r in all_recipes:
            if r.check(state):
                have_recipe = 1

        if have_recipe == 0:
            #for r in all_recipes:
            for name, rule in Crafting['Recipes'].items():
                objects = {}
                try:
                    objects.update(rule['Produces'])
                except:
                    pass
                for key, value in objects.items():
                    if state.get(key) > 0:  #if I have this item
                        # I have the produce, just don't have the required item
                        # update state here
                        required_object  = list(rule['Requires'])[0]
                        state[required_object] = 1
                        return state
        return state

    return requirment

def goal_regression_search(graph_regression, state, is_goal_regression, limit, heuristic):
    # TODO: add time limit here for backward search

    frontier = []
    heappush(frontier, (0, state))
    came_from = {}
    cost_so_far = {}
    came_from[state] = None
    cost_so_far[state] = 0
    current_state = None
    names = {}
    names[state] = None

    #while not len(frontier) == 0:
    while True:
        #old_cost, old_state = heappop(frontier)
        old_state = state

        if is_goal_regression(old_state):  # if at waypoint stop
            # came_from[next_pos] = current
            current_state = old_state
            break
        # if graph_regression can't find a recipe to work on yet, we add the requirement
        # update state
        old_state = requirement_checker(old_state)
        # go through all recipes, can we make
        for next in graph_regression(old_state):  # neighbors
            next_name, next_state, next_cost = next

            # new_cost = next_cost + old_cost
            # if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
            #     cost_so_far[next_state] = new_cost
            #     #priority = new_cost + heuristic(next_state)
            #     priority = new_cost + 0
            #     heappush(frontier, (priority, next_state))
            #     names[next_state] = next_name
            #     # frontier.put(next_pos, priority)
            #     came_from[next_state] = old_state

            names[next_state] = next_name

            came_from[next_state] = old_state



    # construct path from came_from
    if not is_goal_regression(current_state):
        print("NO PATH FOUND")
        return None

    path = [(current_state, "end")]

    came_from_reversed = {v: k for k, v in came_from.items()}  # reverse came_from
    names_reversed = {v: k for k, v in names.items()}  # reverse names

    node = current_state
    while node != None:
        path = [(node, names_reversed[node])] + path
        node = came_from_reversed[node]
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
        # Forward Search
        checker = make_checker(rule)
        effector = make_effector(rule)

        # Backward Search
        checker = make_checker_regression(rule)
        requirement_checker = check_requiremnt(rule)
        effector = make_effector_regression(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # # # Forward Search Implementation
    # # Create a function which checks for the goal
    # is_goal = make_goal_checker(Crafting['Goal'])
    #
    # # Initialize first state from initial inventory
    # state = State({key: 0 for key in Crafting['Items']})
    # state.update(Crafting['Initial'])
    #
    # # Search for a solution
    # resulting_plan = search(graph, state, is_goal, 30, heuristic)
    #
    # if resulting_plan:
    #     # Print resulting plan
    #     for state, action in resulting_plan:
    #         print('\t', state)
    #         print(action)

    # # Backward Search Implementation
    # Create a function which checks for the initial (goal in regression)
    is_goal_regression = make_goal_checker_regression(Crafting['Initial'])

    # Initialize first state from goal inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Goal'])

    # Search for a solution
    resulting_plan_regression = goal_regression_search(graph_regression, state, is_goal_regression, 30, heuristic)

    # print plan
    if resulting_plan_regression:
        # Print resulting plan
        for state, action in resulting_plan_regression:
            print('\t', state)
            print(action)
