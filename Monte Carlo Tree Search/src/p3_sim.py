import sys
from timeit import default_timer as time
import p3_t3
import mcts_vanilla
import mcts_modified
import random_bot
import rollout_bot

players = dict(
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

rounds = 100
wins = {'draw':0, 1:0, 2:0}

start = time()  # To log how much time the simulation takes.
for i in range(rounds):

    print("")
    print("Round %d, fight!" % i)

    state = state0
    last_action = None
    current_player = player1
    while not board.is_ended(state):
        last_action = current_player(board, state)
        state = board.next_state(state, last_action)
        current_player = player1 if current_player == player2 else player2
    print("Finished!")
    print()
    final_score = board.points_values(state)
    winner = 'draw'
    if final_score[1] == 1:
        winner = 1
    elif final_score[2] == 1:
        winner = 2
    print("The %s bot wins this round! (%s)" % (winner, str(final_score)))
    wins[winner] = wins.get(winner, 0) + 1

print("")
print("Final win counts:", dict(wins))

# Also output the time elapsed.
end = time()
print(end - start, ' seconds')
