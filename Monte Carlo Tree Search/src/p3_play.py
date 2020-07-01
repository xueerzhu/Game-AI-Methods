import sys
import p3_t3
import mcts_vanilla
import mcts_modified
import random_bot
import rollout_bot

def get_human_input(board, state):
    move = input("Which move? BoardY BoardX SquareY SquareX (or q to quit) ").strip()
    if move == "q":
    	exit(2)
    action = board.pack_action(move)
    if board.is_legal(state, action):
        return action
    else:
        print("Please input moves as space-separated lists of numbers.  Remember that you can only move in the board corresponding to your opponent's last move!")
        return get_human_input(board, state)

players = dict(
    human=get_human_input,
    random_bot=random_bot.think,
    rollout_bot=rollout_bot.think,
    mcts_vanilla=mcts_vanilla.think,
    mcts_modified=mcts_modified.think
)

board = p3_t3.Board()
state0 = board.starting_state()

if len(sys.argv) != 3:
    print("Need two player arguments")
    exit(1)

p1 = sys.argv[1]
if p1 not in players:
    print("p1 not in "+players.keys().join(","))
    exit(1)
p2 = sys.argv[2]
if p2 not in players:
    print("p2 not in "+players.keys().join(","))
    exit(1)

player1 = players[p1]
player2 = players[p2]
state = state0
last_action = None
current_player = player1
while not board.is_ended(state):
    print(board.display(state, last_action))
    print("Player "+str(board.current_player(state)))
    last_action = current_player(board, state)
    state = board.next_state(state, last_action)
    current_player = player1 if current_player == player2 else player2
print("Finished!")
print(board.points_values(state))
