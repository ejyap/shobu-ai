import numpy as np
import copy
from time import time

BLACK = 1
EMPTY = 0
WHITE = -1

WIDTH = 4
HEIGHT = 4

ACTIONS = [(-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0),
           (-2, 2), (0, 2), (2, 2), (2, 0), (2, -2), (0, -2), (-2, -2), (-2, 0)]

def checkBounds(position):
    x, y = position
    return x < HEIGHT and x >= 0 and y < WIDTH and y >= 0

def getPosition(index):
    return (index//HEIGHT, index%WIDTH)

class ShobuGame:

    '''ShobuGame provides the necessary abstractions for an agent to play the game. It simply keeps track of
    the current board state and possible moves from the current state.'''

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = Board()

    def make_move(self, move):
        self.state = self.state.make_move(move)

    def get_moves(self):
        if self.state:
            return self.state.get_valid_moves()
        return []

    def get_winner(self):
        return self.state.winner

    def get_turn_player(self):
        return self.state.player


class Move:
    '''Move defines an action. first_board specifies the board and first_source specifies the board position of the
    stone to be moved as part of the passive move. second_board and second_source characterize the offensive move.
    The board variables can be a number between 0 and 3, specifying the board number. The source variables are tuples,
    specifying the coordinate of the stone to be moved at the specified board number.'''

    def __init__(self, first_board, first_source, second_board, second_source, action):
        self.first_board = first_board
        self.first_source = first_source
        self.action = action
        self.second_board = second_board
        self.second_source = second_source

    def __hash__(self):
        hash_value1 = self.first_board + self.first_source[0] * 10 + self.first_source[1] * 100 + self.action[0] * 1000
        +self.action[1] * 10000

        hash_value2 = 0

        if self.second_board:
            hash_value2 += self.second_board + self.second_source[0] * 10 + self.second_source[1] * 100

        return hash((hash_value1, hash_value2))

    def __repr__(self):
        rep = 'Move stone at {} to {} in board {}.'.format(self.first_source, self.action, self.first_board)
        if self.second_source:
            rep += ' Move stone at {} to {} in board {}.'.format(self.second_source, self.action, self.second_board)
        return rep


class Board:

    '''Board represents a game state. A game state is characterized by a (4, 4, 4) numpy array. The first dimension
     represents the 4 boards. The boards 0 and 1 represent the WHITE home boards, and the boards 2 and 3 represent the
     BLACK home boards. The second and third dimensions represent the 16 cells in a board. Each cell is one of 3
    possible values: 0 (Empty cell), 1 (Black stone), -1 (White stone). A state is also characterized by the current turn
    player and by the winner at a given state (if there is one).'''

    def __init__(self, boards=None, player=1, winner=0):
        if boards is None:
            boards = np.zeros((4, HEIGHT, WIDTH))
            boards[:, 0, :] = WHITE
            boards[:, 3, :] = BLACK
            self.boards = boards
        else:
            self.boards = boards
        self.player = player
        self.winner = winner

    def check_goal_state(self):
        '''
        Determine whether the current state is a goal sate and if so, returns the winner.
        :return: -1 (White wins), 0 (No winner), 1 (Black wins).
        '''

        for board in self.boards:
            if 1 not in set(board.flatten()):
                return -1
            if -1 not in set(board.flatten()):
                return 1
        return 0

    def does_move_capture(self, move):
        '''Check if a move capture any opponent's piece. Returns tuple with (False, None) if move does not capture, and
        (True, position) if move captures, where position is the position of the captured stone.'''
        if move.second_board == None:
            return (False, None)

        board2 = self.boards[move.second_board]
        second_piece = board2[move.second_source]
        x, y = move.second_source
        _x, _y = move.action
        xm, ym = 0, 0

        if _x != 0:
            xm += _x // abs(_x)
        if _y != 0:
            ym += _y // abs(_y)

        piece_to_push = None

        if board2[(x + xm, y + ym)] == second_piece * -1:
            piece_to_push = (x + xm, y + ym)

        if piece_to_push:
            if not checkBounds((x + 2 * xm, y + 2 * ym)):
                return (True, piece_to_push)

        if abs(_x) == 2 or abs(_y) == 2:
            if board2[(x + 2 * xm, y + 2 * ym)] == second_piece * -1:
                piece_to_push = (x + 2 * xm, y + 2 * ym)
            if piece_to_push:
                if not checkBounds((x + 3 * xm, y + 3 * ym)):
                    return (True, piece_to_push)
        return (False, None)

    # Check if a passive move is legal
    def validate_passive_move(self, board_index, source, action, player=None):
        if not player:
            player = self.player
        board1 = self.boards[board_index]

        x, y = source
        first_piece = board1[source]
        if not first_piece or first_piece != player:
            return False

        # Determine whether moving a stone 1 step into a direction is valid.
        xm, ym = 0, 0
        _x, _y = action
        if _x != 0:
            xm += _x // abs(_x)
        if _y != 0:
            ym += _y // abs(_y)

        # Check if the desired position is out of bounds.
        if not checkBounds((x + xm, y + ym)):
            return False

        # Check if there's already a stone in the desired square.
        if board1[(x + xm, y + ym)]:
            return False

        # Determine whether moving a stone 2 steps into a direction is valid.
        if abs(_x) == 2 or abs(_y) == 2:
            if not checkBounds((x + 2 * xm, y + 2 * ym)):
                return False

            if board1[(x + 2 * xm, y + 2 * ym)]:
                return False
        return True

    # Check if an offensive move is legal
    def validate_offensive_move(self, board_index, source, action, player=None):
        if not player:
            player = self.player
        if board_index is None or source is None:
            return True
        board2 = self.boards[board_index]
        x, y = source
        second_piece = board2[source]

        if not second_piece or second_piece != player:
            return False

        xm, ym = 0, 0
        _x, _y = action
        if _x != 0:
            xm += _x // abs(_x)
        if _y != 0:
            ym += _y // abs(_y)

        if not checkBounds((x + xm, y + ym)):
            return False

        # Can't push/attack your own stone, so invalid.
        if board2[(x + xm, y + ym)] == second_piece:
            return False

        # If you push an enemy stone, another enemy stone can't be behind it
        if board2[(x + xm, y + ym)] and checkBounds((x + 2 * xm, y + 2 * ym)) and \
                board2[(x + 2 * xm, y + 2 * ym)]:
            return False

        if abs(_x) == 2 or abs(_y) == 2:
            if not checkBounds((x + 2 * xm, y + 2 * ym)):
                return False

            if board2[(x + 2 * xm, y + 2 * ym)] == second_piece:
                return False

            if board2[(x + xm, y + ym)] and checkBounds((x + 3 * xm, y + 3 * ym)) and \
                    board2[(x + 3 * xm, y + 3 * ym)]:
                return False

            if board2[(x + 2 * xm, y + 2 * ym)] and checkBounds((x + 3 * xm, y + 3 * ym)) and \
                    board2[(x + 3 * xm, y + 3 * ym)]:
                return False
        return True

    def validate_board_indices(self, board_index1, board_index2, player=None):
        if board_index1 == board_index2:
            return False

        if not player:
            player = self.player
        if player == BLACK:
            if board_index1 == 2:
                if board_index2 == 0:
                    return False
            elif board_index1 == 3:
                if board_index2 == 1:
                    return False
            else:
                return False

        if player == WHITE:
            if board_index1 == 0:
                if board_index2 == 2:
                    return False
            elif board_index1 == 1:
                if board_index2 == 3:
                    return False
            else:
                return False
        return True

    def validate_move(self, move, validate_board_indices=True):
        '''
        Determines whether the move is valid based on various conditions.
        :param move: Move
        :return: True/False
        '''

        first_source = move.first_source
        first_board = move.first_board
        second_source = move.second_source
        second_board = move.second_board
        action = move.action

        if validate_board_indices == True:
            return self.validate_board_indices(first_board, second_board) and \
                   self.validate_offensive_move(second_board, second_source, action) and \
                   self.validate_passive_move(first_board, first_source, action)
        else:
            return self.validate_offensive_move(second_board, second_source, action) and \
                   self.validate_passive_move(first_board, first_source, action)
        # Defensive Move. Player is only allowed to move to an unoccupied space and cannot attack any stone

    def get_valid_moves(self, player=None):
        '''
        Return all valid moves that current player can perform.
        :param player: 0 or 1. 0 is BLACK player. 1 is WHITE player.
        :return: Move list.
        '''

        if player == None:
            player = self.player

        moves = []

        board_indices1 = (2, 3) if player == BLACK else (0, 1)

        # Set that records the pieces positions, don't validate passive moves that lead to these positions.
        visited_pieces = set()
        for i in board_indices1:
            board1 = self.boards[i]
            # Determine the indices of boards for offensive move
            if i == 0 or i == 2:
                board_indices2 = (1, 3)
            elif i == 1 or i == 3:
                board_indices2 = (0, 2)

            possible_offensive_moves = {action: [] for action in ACTIONS}

            for j in board_indices2:
                q = 0
                board2 = self.boards[j]
                for piece2 in board2.flatten():
                    if piece2:
                        x2, y2 = getPosition(q)
                        visited_pieces.add((x2, y2, j))
                        if player == piece2:
                            for _x, _y in ACTIONS:
                                if x2 + _x < 0 or x2 + _x > 3 or y2 + _y < 0 or y2 + _y > 3:
                                    continue
                                if self.validate_offensive_move(j, (x2, y2), (_x, _y), player=player):
                                    possible_offensive_moves[(_x, _y)].append(((x2, y2), j))
                    q += 1

            p = 0
            for piece1 in board1.flatten():
                if piece1:
                    x, y = getPosition(p)
                    visited_pieces.add((x, y, i))
                    if player == piece1:
                        for _x, _y in ACTIONS:
                            if x + _x < 0 or x + _x > 3 or y + _y < 0 or y + _y > 3:
                                continue
                            if (x + _x, y + _y, i) in visited_pieces:
                                continue
                            if self.validate_passive_move(i, (x, y), (_x, _y), player=player):
                                # Avoid reaching this expensive piece of code as much as possible.
                                for offensive_move in possible_offensive_moves[(_x, _y)]:
                                    if self.validate_board_indices(i, offensive_move[0], player=player):
                                        possible_move = Move(i, (x, y), offensive_move[1], offensive_move[0], (_x, _y))
                                        moves.append(possible_move)
                p += 1
        # If there are no legal offensive moves.
        if len(moves) == 0:
            for i in board_indices1:
                board1 = self.boards[i]
                p = 0
                for piece1 in board1.flatten():
                    if piece1 and player == piece1:
                        x, y = getPosition(p)
                        for _x, _y in ACTIONS:
                            if x + _x < 0 or x + _x > 3 or y + _y < 0 or y + _y > 3:
                                continue
                            if (x + _x, y + _y, i) in visited_pieces:
                                continue
                            if self.validate_passive_move(i, (x, y), (_x, _y), player=player):
                                possible_move = Move(i, (x, y), None, None, (_x, _y))
                                moves.append(possible_move)
                    p += 1
        return moves

    def make_move(self, move):

        board = self

        board1 = board.boards[move.first_board]
        x, y = move.first_source
        _x, _y = move.action

        board1[(x + _x, y + _y)] = board1[(x, y)]
        board1[(x, y)] = EMPTY

        if move.second_source is None:
            board.player = board.player * -1
            board.winner = board.check_goal_state()
            return board

        board2 = board.boards[move.second_board]
        second_piece = board2[move.second_source]
        x, y = move.second_source
        _x, _y = move.action
        xm, ym = 0, 0

        if _x != 0:
            xm += _x // abs(_x)
        if _y != 0:
            ym += _y // abs(_y)

        piece_to_push = None

        if board2[(x + xm, y + ym)] == second_piece * -1:
            piece_to_push = (x + xm, y + ym)

        if piece_to_push:
            if checkBounds((x + 2 * xm, y + 2 * ym)):
                board2[(x + 2 * xm, y + 2 * ym)] = second_piece * -1
            board2[piece_to_push] = 0

        if abs(_x) == 2 or abs(_y) == 2:
            if board2[(x + 2 * xm, y + 2 * ym)] == second_piece * -1:
                piece_to_push = (x + 2 * xm, y + 2 * ym)
            if piece_to_push:
                if checkBounds((x + 3 * xm, y + 3 * ym)):
                    board2[(x + 3 * xm, y + 3 * ym)] = second_piece * -1
                board2[piece_to_push] = 0

        board2[(x + _x, y + _y)] = board2[(x, y)]
        board2[(x, y)] = EMPTY

        board.player = board.player * -1
        board.winner = board.check_goal_state()

        return board

    def __repr__(self):
        str_rep = ''

        for b in range(2):
            board1 = self.boards[b * 2]
            board2 = self.boards[b * 2 + 1]
            str_rep += '-BLACK-'
            str_rep += '   '
            str_rep += '-WHITE-\n'

            for i in range(HEIGHT):
                for j in range(WIDTH):
                    piece = board1[(i, j)]
                    if piece == EMPTY:
                        str_rep += '* '
                    elif piece == BLACK:
                        str_rep += 'o '
                    elif piece == WHITE:
                        str_rep += 'x '
                str_rep += '  '
                for j in range(WIDTH):
                    piece = board2[(i, j)]
                    if piece == EMPTY:
                        str_rep += '* '
                    elif piece == BLACK:
                        str_rep += 'o '
                    elif piece == WHITE:
                        str_rep += 'x '
                str_rep += '\n'
            if b == 0:
                str_rep += '-----------------\n'
        return str_rep