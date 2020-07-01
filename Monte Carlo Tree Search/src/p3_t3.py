# Copyright (c) 2014 Jeff Bradberry

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

num_players = 2

positions = dict(
    ((r, c), 1 << (3 * r + c))
    for r in range(3)
    for c in range(3)
)

inv_positions = dict(
    (v, P) for P, v in positions.items()
)

class Board(object):
    wins = [
        positions[(r, 0)] | positions[(r, 1)] | positions[(r, 2)]
        for r in range(3)
    ] + [
        positions[(0, c)] | positions[(1, c)] | positions[(2, c)]
        for c in range(3)
    ] + [
        positions[(0, 0)] | positions[(1, 1)] | positions[(2, 2)],
        positions[(0, 2)] | positions[(1, 1)] | positions[(2, 0)],
    ]

    def starting_state(self):
        # Each of the 9 pairs of player 1 and player 2 board bitmasks
        # plus the win/tie state of the big board for p1 and p2 plus
        # the row and column of the required board for the next action
        # and finally the player number to move.
        return (0, 0) * 10 + (None, None, 1)

    def display(self, state, action, _unicode=True):
        actions = dict(
            ((R, C, r, c), p)
            for R in range(3)
            for C in range(3)
            for r in range(3)
            for c in range(3)
            for i, p in enumerate([' X ', ' O '])
            if state[2 * (3 * R + C) + i] & positions[(r, c)]
        )

        player = state[-1]

        sub = u"\u2564".join(u"\u2550\u2550\u2550" for x in range(3))
        top = u"\u2554" + u"\u2566".join(sub for x in range(3)) + u"\u2557\n"

        sub = u"\u256a".join(u"\u2550\u2550\u2550" for x in range(3))
        div = u"\u2560" + u"\u256c".join(sub for x in range(3)) + u"\u2563\n"

        sub = u"\u253c".join(u"\u2500\u2500\u2500" for x in range(3))
        sep = u"\u255f" + u"\u256b".join(sub for x in range(3)) + u"\u2562\n"

        sub = u"\u2567".join(u"\u2550\u2550\u2550" for x in range(3))
        bot = u"\u255a" + u"\u2569".join(sub for x in range(3)) + u"\u255d\n"
        if action:
            bot += u"Last played: {0}\n".format(self.unpack_action(action))
        bot += u"Player: {0}\n".format(player)

        return (
            top +
            div.join(
                sep.join(
                    u"\u2551" +
                    u"\u2551".join(
                        u"\u2502".join(
                            actions.get((R, C, r, c), "   ") for c in range(3)
                        )
                        for C in range(3)
                    ) +
                    u"\u2551\n"
                    for r in range(3)
                )
                for R in range(3)
            ) +
            bot
        )

    def pack_state(self, data):
        state = [0] * 20
        state.extend([data['constraint']['outer-row'],
                      data['constraint']['outer-column'],
                      data['player']])

        for item in data['pieces']:
            R, C, player = item['outer-row'], item['outer-column'], item['player']
            r, c = item['inner-row'], item['inner-column']
            state[2 * (3 * R + C) + player - 1] += 1 << (3 * r + c)

        for item in data['boards']:
            players = (1, 2)
            if item['player'] is not None:
                players = (item['player'],)

            for player in players:
                state[17 + player] += 1 << (3 *
                                            item['outer-row'] + item['outer-column'])

        return tuple(state)

    def unpack_state(self, state):
        player = state[-1]
        p1_boards, p2_boards = state[18], state[19]

        pieces, boards = [], []
        for R in range(3):
            for C in range(3):
                for r in range(3):
                    for c in range(3):
                        index = 1 << (3 * r + c)

                        if index & state[2 * (3 * R + C)]:
                            pieces.append({
                                'player': 1, 'type': 'X',
                                'outer-row': R, 'outer-column': C,
                                'inner-row': r, 'inner-column': c,
                            })
                        if index & state[2 * (3 * R + C) + 1]:
                            pieces.append({
                                'player': 2, 'type': 'O',
                                'outer-row': R, 'outer-column': C,
                                'inner-row': r, 'inner-column': c,
                            })

                board_index = 1 << (3 * R + C)
                if board_index & p1_boards & p2_boards:
                    boards.append({
                        'player': None, 'type': 'full',
                        'outer-row': R, 'outer-column': C,
                    })
                elif board_index & p1_boards:
                    boards.append({
                        'player': 1, 'type': 'X',
                        'outer-row': R, 'outer-column': C,
                    })
                elif board_index & p2_boards:
                    boards.append({
                        'player': 2, 'type': 'O',
                        'outer-row': R, 'outer-column': C,
                    })

        return {
            'pieces': pieces,
            'boards': boards,
            'constraint': {'outer-row': state[20], 'outer-column': state[21]},
            'player': player,
            'previous_player': 3 - player,
        }

    def pack_action(self, notation):
        try:
            R, C, r, c = map(int, notation.split())
        except Exception:
            return
        return R, C, r, c

    def unpack_action(self, action):
        try:
            return '{0} {1} {2} {3}'.format(*action)
        except Exception:
            return ''

    def display_action(self, action):
        return self.unpack_action(action)

    def next_state(self, state, action):
        R, C, r, c = action
        player = state[-1]
        board_index = 2 * (3 * R + C)
        player_index = player - 1

        state = list(state)
        state[-1] = 3 - player
        state[board_index + player_index] |= positions[(r, c)]
        updated_board = state[board_index + player_index]

        full = (state[board_index] | state[board_index + 1] == 0x1ff)
        if any(updated_board & w == w for w in self.wins):
            state[18 + player_index] |= positions[(R, C)]
        elif full:
            state[18] |= positions[(R, C)]
            state[19] |= positions[(R, C)]

        if (state[18] | state[19]) & positions[(r, c)]:
            state[20], state[21] = None, None
        else:
            state[20], state[21] = r, c

        return tuple(state)

    def is_legal(self, state, action):
        R, C, r, c = action

        # Is action out of bounds?
        if (R, C) not in positions:
            return False
        if (r, c) not in positions:
            return False

        player = state[-1]
        board_index = 2 * (3 * R + C)
        player_index = player - 1

        # Is the square within the sub-board already taken?
        occupied = state[board_index] | state[board_index + 1]
        if positions[(r, c)] & occupied:
            return False

        # Is this particular board won already?
        finished = state[18] | state[19]
        if finished & positions[(R,C)]:
            return False
        
        # Is our action unconstrained by the previous action?
        if state[20] is None:
            return True

        # Otherwise, we must play in the proper sub-board.
        return (R, C) == (state[20], state[21])

    def legal_actions(self, state):
        R, C = state[20], state[21]
        Rset, Cset = (R,), (C,)
        if R is None:
            Rset, Cset = range(3), range(3)

        occupied = [
            state[2 * x] | state[2 * x + 1] for x in range(9)
        ]
        finished = state[18] | state[19]

        actions = [
            (R, C, r, c)
            for R in Rset
            for C in Cset
            for r in range(3)
            for c in range(3)
            if not occupied[3 * R + C] & positions[(r, c)]
            and not finished & positions[(R, C)]
        ]

        return actions

    def previous_player(self, state):
        return 3 - state[-1]

    def current_player(self, state):
        return state[-1]

    def is_ended(self, state):
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        if any(w & p1 == w for w in self.wins):
            return True
        if any(w & p2 == w for w in self.wins):
            return True
        if state[18] | state[19] == 0x1ff:
            return True

        return False

    def win_values(self, state):
        if not self.is_ended(state):
            return
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        if any(w & p1 == w for w in self.wins):
            return {1: 1, 2: 0}
        if any(w & p2 == w for w in self.wins):
            return {1: 0, 2: 1}
        if state[18] | state[19] == 0x1ff:
            return {1: 0.5, 2: 0.5}

    def owned_boxes(self, state):
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]
        ret = {}
        for y in range(3):
            for x in range(3):
                if p1 & positions[(y,x)]:
                    ret[(y,x)] = 1
                elif p2 & positions[(y,x)]:
                    ret[(y,x)] = 2
                else:
                    ret[(y,x)] = 0
        return ret
        
    def points_values(self, state):
        if not self.is_ended(state):
            return
        p1 = state[18] & ~state[19]
        p2 = state[19] & ~state[18]

        if any(w & p1 == w for w in self.wins):
            return {1: 1, 2: -1}
        if any(w & p2 == w for w in self.wins):
            return {1: -1, 2: 1}
        if state[18] | state[19] == 0x1ff:
            return {1: 0, 2: 0}

    def winner_message(self, winners):
        winners = sorted((v, k) for k, v in winners.items())
        value, winner = winners[-1]
        if value == 0.5:
            return "Draw."
        return "Winner: Player {0}.".format(winner)
