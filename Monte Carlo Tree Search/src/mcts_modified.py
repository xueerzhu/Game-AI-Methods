
from mcts_node import MCTSNode
from random import choice
from math import sqrt, log

num_nodes = 10
constant_for_heuristic_explore = 4
depth_allowed = 5
roll_attempts = 12

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    
    # if node is not yet tried, try it
    if (node.untried_actions):
        return node, state
    # else if, the node does not have child nodes try it
    elif (not node.child_nodes):
        return node, state
    # else, use UCT as a heuristic to find promising nodes to try
    else:
        player = board.current_player(state)
        # use UCT with heuristic
        best_node = UCT(node, player)
        state = board.next_state(state, best_node.parent_action)
        return traverse_nodes(best_node, board, state, player)


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    
    # if does not have untried actions check to see if it has children
    if (not node.untried_actions):
        if (not node.child_nodes):
            return node, state
    # try an untried action in current node
    random_action = choice(node.untried_actions)
    state = board.next_state(state, random_action)
    next_node = MCTSNode(parent = node, parent_action = random_action, action_list = board.legal_actions(state))
    # remove untried action from the node
    node.untried_actions.remove(random_action)
    # set new child as a leaf of current node
    node.child_nodes[random_action] = next_node
    # return the new leaf node and the state
    return next_node, state


def rollout(board, state, identity):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    
    # use average to determine better moves
    average = 0
    # for the attempts allowed, run a simluated game
    for i in range(1, roll_attempts + 1):
        simulation = state
        # for the depth allowed, simulate
        for k in range(depth_allowed):
            # if board ends, break
            if (board.is_ended (simulation)):
                break
            # try a random action from legal moves
            random_action = choice(board.legal_actions(state))
            # move the simulation along
            simulation = board.next_state(simulation, random_action)
        # calculate average to gauge success rates
        average = average * ((i - 1) / i) + outcome(board, simulation, identity) * (1 / i)    
    return average


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    
    # until the root is reached (root_node.parent == None) go the the current node's parent
    while node != None:
        # increment node wins and visists to give more weight to successful branches
        node.wins = node.wins + won
        node.visits = node.visits + 1
        node = node.parent
    return


def think(board, state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action to be taken.

    """
    
    identity_of_bot = board.current_player(state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(state))

    for step in range(num_nodes):
        # Copy the game for sampling a playthrough
        sampled_game = state  # reset state to exclude newly expanded leaf

        # Start at root
        node = root_node

        # Do MCTS - This is all you!
        leaf = traverse_nodes(node, board, sampled_game, identity_of_bot)  # current leaf
        
        # Expansion
        current, sampled_game = traverse_nodes(node, board, sampled_game, identity_of_bot)
        new_leaf, sampled_game  = expand_leaf(current, board, sampled_game)  # expand to a new leaf
        
        # use heuristic to make more intelligent moves
        heuristic_think = rollout(board, sampled_game, identity_of_bot)
        
        # Backpropagate
        backpropagate(new_leaf, heuristic_think)
    
    new_leaf = choice(list(root_node.child_nodes.values()))
    optimal_winAmount = 0
    # for each child of the root determine win ratios to converges towards better moves
    for child in root_node.child_nodes.values():
        # obtain ratio of wins compared to visits
        winAmount = child.wins / child.visits
        # if the win amount of the node is better than the previously best amount
        # set the new_leaf to be the child of the better performing node and 
        # update the optimal win amount to see if another is better
        if (winAmount > optimal_winAmount):
            optimal_winAmount = winAmount
            new_leaf = child
    # return the best found action which will be the parent of the new leaf node
    return new_leaf.parent_action

# UCT, upper confidence bounds (UCB1), adopted from: https://www.chessprogramming.org/UCT
# heuristic used to improve upon mcts_vanilla.py
# uses a UCT_value from the formula to help the agent choose more favorable moves that lead to more favorable outcomes
def UCT(node, opponent):
    # chose one of the children of the current node to try out
    best = choice(list(node.child_nodes.values()))
    max = 0
    # for each child of the current node, use the heuristic to find the optimal node with the best success rate
    for child in node.child_nodes.values():
        # initialize heuristic
        heuristic = 0.5 * child.visits
        # if move favors opponent discourage heuristic for this current node
        heuristic = heuristic + -child.wins if opponent else child.wins
        # using formula from the website above, determine its worthyness compared to the other nodes
        UCT_value = (heuristic / child.visits) + constant_for_heuristic_explore * (sqrt(log(child.parent.visits) / child.visits))
        # if it performs better than a previously tested node, update the best node to this one, and
        # update the max value to be the new highest performing value
        if (UCT_value > max):
            max = UCT_value
            best = child
    # return the most promising child node
    return child

# get score from the players of current state, returns the difference of the current player's and the opponent's sampled_game score
# modified from rollout_bot.py (original function is "outcome")
def outcome(board, state, identity):
    player_scores = board.points_values(state)
    player_controlled_boxes = board.owned_boxes(state)
    if player_scores is not None:
        player1_score = player_scores[1]*9
        player2_score = player_scores[2]*9
    else:
        player1_score = len([v for v in player_controlled_boxes.values() if v == 1])
        player2_score = len([v for v in player_controlled_boxes.values() if v == 2])
    return player1_score - player2_score if identity == 1 else player1_score - player2_score