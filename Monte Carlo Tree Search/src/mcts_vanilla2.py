
from mcts_node import MCTSNode
#from random import choice, random
import random
from math import sqrt, log

# num_nodes = 1000
num_nodes = 50
explore_faction = 2

def traverse_nodes(node, board, state, identity):
    """ Traverses the tree until the end criterion are met.

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 'red' or 'blue'.

    Returns:        A node from which the next stage of the search can proceed.

    """
    current = node
    while len(current.child_nodes) > 0:  # if not leaf
        current_best_value = 0
        children = list(current.child_nodes.values())
        current_best_child = children[0]
        # Select the best child of its children
        # balancing exploration and exploitation
        for child in children:  # get child
            Q = child.wins / (1 + child.visits)  # exploitation
            U = sqrt(child.parent.visits) * (child.parent.wins / (1 + child.parent.visits)) / (1 + child.visits)  # exploration
            value = Q + U
            if value > current_best_value:
                current_best_value = value
                current_best_child = child
        current = current_best_child

    return current


def expand_leaf(node, board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node.

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:    The added child node.

    """
    moves = board.legal_actions(state)
    if len(moves) > 0:
        move = moves[0]  # pop first untried action
        new_state = board.next_state(state, move)
        new_node = MCTSNode(parent=node, parent_action=move, action_list=board.legal_actions(new_state))
        node.child_nodes[move] = new_node
    else:
        new_node = None
    return new_node


def rollout(board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.

    """
    moves = board.legal_actions(state)
    move = moves[0]
    rollout_state = board.next_state(state, move)

    # Plays until game ends
    while not board.is_ended(rollout_state):
        rollout_move = random.choice(board.legal_actions(rollout_state))
        rollout_state = board.next_state(rollout_state, rollout_move)


def backpropagate(node, won):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    current = node
    while current.parent is not None:
        current.visits += 1
        if won:
            current.wins += 1
        current = current.parent


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
        # Selection
        leaf = traverse_nodes(node, board, sampled_game, identity_of_bot)  # current leaf

        # Expansion
        new_leaf = expand_leaf(leaf, board, sampled_game)  # expand to a new leaf
        sampled_game = board.next_state(sampled_game, new_leaf.parent_action)

        # Rollout
        if not board.is_ended(sampled_game):
            rollout(board, sampled_game)  # play the game

        # who wins
        score = board.points_values(sampled_game)
        winner = 'draw'
        if score is not None:
            if score[1] == 1:
                winner = 1
            elif score[2] == 1:
                winner = 2
            if winner is identity_of_bot:
                i_won = 1
            else:
                i_won = 0
            backpropagate(leaf, i_won)  # back up using i_won condition

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_child = max(root_node.child_nodes.items(), key=lambda item: item[1].visits)[1]  # most frequently visited
    best_move = best_child.parent_action

    return best_move

