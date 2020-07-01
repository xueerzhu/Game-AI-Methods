

class MCTSNode:
    def __init__(self, parent=None, parent_action=None, action_list=[]):
        """ Initializes the tree node for MCTS. The node stores links to other nodes in the tree (parent and child
        nodes), as well as keeps track of the number of wins and total simulations that have visited the node.

        Args:
            parent:         The parent node of this node.
            parent_action:  The action taken from the parent node that transitions the state to this node.
            action_list:    The list of legal actions to be considered at this node.

        """
        self.parent = parent                    # Parent node to this node
        self.parent_action = parent_action      # The move that got us to this node - "None" for the root node.

        self.child_nodes = {}                   # Action -> MCTSNode dictionary of children
        self.untried_actions = action_list      # Yet unexplored actions

        self.wins = 0                           # Total wins of all paths through this node.
        self.visits = 0                         # Number of times this node has been visited.

    def __repr__(self):
        """
        This method provides a string representing the node. Any time str(node) is used, this method is called.
        """
        return ' '.join(["[", str(self.parent_action),
                         "Win rate:", "{0:.0f}%".format(100 * self.wins / self.visits),
                         "Visits:", str(self.visits),  "]"])

    def tree_to_string(self, horizon=1, indent=0):
        """ This method returns a string of the tree down to a defined horizon. The string is recursively constructed.

        Args:
            horizon:    The cutoff depth for including tree nodes.
            indent:     A recursive parameter that informs the process of how far a node should be indented.

        Returns:        A string representing the tree to a given depth.

        """
        string = ''.join(['| ' for i in range(indent)]) + str(self) + '\n'
        if horizon > 0:
            for child in self.child_nodes.values():
                string += child.tree_to_string(horizon - 1, indent + 1)
        return string
