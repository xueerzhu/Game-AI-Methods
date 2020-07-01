import random

ROLLOUTS = 10
MAX_DEPTH = 5


def think(board, state):
    """ For each possible move, this bot plays ROLLOUTS random games to depth MAX_DEPTH then averages the
    score as an estimate of how good the move is.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:    The action with the maximal score given the rollouts.

    """
    moves = board.legal_actions(state)

    best_move = moves[0]
    best_expectation = float('-inf')

    me = board.current_player(state)

    # Define a helper function to calculate the difference between the bot's score and the opponent's.
    def outcome(owned_boxes, game_points):
        if game_points is not None:
            # Try to normalize it up?  Not so sure about this code anyhow.
            red_score = game_points[1]*9
            blue_score = game_points[2]*9
        else:
            red_score = len([v for v in owned_boxes.values() if v == 1])
            blue_score = len([v for v in owned_boxes.values() if v == 2])
        return red_score - blue_score if me == 1 else blue_score - red_score

    for move in moves:
        total_score = 0.0

        # Sample a set number of games where the target move is immediately applied.
        for r in range(ROLLOUTS):
            rollout_state = board.next_state(state, move)

            # Only play to the specified depth.
            for i in range(MAX_DEPTH):
                if board.is_ended(rollout_state):
                    break
                rollout_move = random.choice(board.legal_actions(rollout_state))
                rollout_state = board.next_state(rollout_state, rollout_move)

            total_score += outcome(board.owned_boxes(rollout_state),
                                   board.points_values(rollout_state))

        expectation = float(total_score) / ROLLOUTS

        # If the current move has a better average score, replace best_move and best_expectation
        if expectation > best_expectation:
            best_expectation = expectation
            best_move = move

    print("Rollout bot picking %s with expected score %f" % (str(best_move), best_expectation))
    return best_move
