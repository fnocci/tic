#!/usr/bin/python

# Flask API that evaluates tic tac toe positions
# and play the next move to win, if possible.

from flask import Flask, abort, request

app = Flask(__name__)

#
# Index the cells in the tic tac toe board like this:
#
# 0 1 2
# 3 4 5
# 6 7 8

# So we can identify the winning sets of indexes like this:
WINS = ({0, 1, 2}, {3, 4, 5}, {6, 7, 8},
        {0, 3, 6}, {1, 4, 7}, {2, 5, 8},
        {0, 4, 8}, {2, 4, 6})

CENTER = 4

CORNERS = {0, 8, 2, 6}

KITTY_CORNERS = {0: 8, 8: 0, 2: 6, 6: 2}

SIDES = {1, 3, 5, 7}

WON = 1


def parse_board(board):
    """ returns None if invalid input """
    # since we're just analyzing one board for potential moves,
    # and not playing a game, re-initialize the board each time

    dboard = {'x': set(), ' ': set(), 'o': set()}

    # check number of places
    if len(board) != 9:
        return None

    # board can only contain one of 3 values
    for i in range(0, 9):
        if   board[i] == ' ':
            dboard[' '].add(i)
        elif board[i] == 'o':
            dboard['o'].add(i)
        elif board[i] == 'x':
            dboard['x'].add(i)
        else:
            return None

    # there needs to be at least one empty space (or more?)
    if len(dboard[' ']) == 0:
        return None

    # number of x's and o's need to differ by one or zero
    dlen = len(dboard['x']) - len(dboard['o'])

    if dlen == 1 or dlen == 0:
        return dboard
    else:
        return None  # it's not our turn, so just bail


def winning (dboard, xo):
    if xo != 'x' and xo != 'o':
        return None
    else:
        for win in WINS:
            if win <= dboard[xo]:
                return WON
        return None


def can_win (dboard, xo):
    if xo != 'x' and xo != 'o':
        return None
    else:
        for win in WINS:
            diffset = win - dboard[xo]
            if len(diffset) == 1:  # we got a winner?
                winner = diffset.pop()
                if winner in dboard[' ']:
                    return winner
    return None


def can_fork (dboard, xo):

    if xo != 'x' and xo != 'o':
        return None

    # so we can check the opposite
    if xo == 'x':
        ox = 'o'
    if xo == 'o':
        ox = 'x'

    # check every blank for its forking potential
    for i in dboard[' ']:
        nthreats = 0

        # first find the winning sets that have i in them
        # check that no element of each i-containing winning set is marked by opponent
        # check that you own at least one element in each i-containing winning set 
        #
        # if all 3 conditions are met at least twice for the same index i,
        # then we can either make or block the potential fork at index i

        for win in WINS:
            if i in win and win.isdisjoint(dboard[ox]) and win & dboard[xo]:
                nthreats += 1

        if nthreats > 1:
            return i

    return None


def trivial_case (dboard):

    # if x has already won, abort
    if winning(dboard, 'x'):
        abort(400)

    # if o has already won, return the same
    # board by returning the index of an 
    # element already marked with a 'o'

    elif winning(dboard, 'o'):
        return dboard['o'].pop()

    #if only one space is blank, play it?
    elif len(dboard[' ']) == 1:
        return dboard[' '].pop()

    #if all the spaces are blank, play the center
    elif len(dboard[' ']) == 9:
        return CENTER

    else:
        return None  # Not Trivial!


# replace the ith letter of board string with an 'o'
def o_ith (board, i):
    b = u""
    a = list(board)
    a[i] = 'o'
    return b.join(a)


@app.route('/tic', methods=['GET'])
def upboard():

    board = request.args.get('board')

    if not board:
        abort(400)

    else:
        dboard = parse_board(board)

    if not dboard:
        abort(400)

    trivial = trivial_case(dboard)

    if trivial is not None:
        return o_ith(board, trivial)

    # Win if you can
    o_wins = can_win(dboard, 'o')

    if o_wins:
        return o_ith(board, o_wins)

    # Block opponent's win
    x_wins = can_win(dboard, 'x')

    if x_wins:
        return o_ith(board, x_wins)

    # Fork if you can
    o_forks = can_fork(dboard, 'o')

    if o_forks:
        return o_ith(board, o_forks)

    # Block the opponent's fork
    x_forks = can_fork(dboard, 'x')

    if x_forks:
        return o_ith(board, x_forks)

    # Play the Center
    if CENTER in dboard[' ']:
        return o_ith(board, CENTER)

    # Play the Opposite Corner
    for i in dboard['x'] & CORNERS:
        if KITTY_CORNERS[i] in dboard[' ']:
            return o_ith(board, KITTY_CORNERS[i])

    # Play Any Empty Corner
    empty_corner = (dboard[' '] & CORNERS).pop()
    if empty_corner:
        return o_ith(board, empty_corner)

    # Play Any Empty Side
    empty_side = (dboard[' '] & SIDES).pop()
    if empty_side:
        return o_ith(board, empty_side)

    # if somehow we got here, bail. 
    abort(400)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
