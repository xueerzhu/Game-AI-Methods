from random import choice

def think(board, state):
    """ Returns a random move. """
    return choice(board.legal_actions(state))
