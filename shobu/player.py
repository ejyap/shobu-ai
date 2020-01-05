from shobu import Move, Board, ShobuGame
from mcts import MonteCarlo, MonteCarloEPT
from minimax import Minimax
from evaluation import stone_advantage, avoid_ones, massive_eval, weighted_value_function, weighted_EPT_value_function
import random

def parse_str_move(str_move):

    try:
        arg_list = list(map(int, str_move.split(',')))
    except:
        return False

    if len(arg_list) != 8:
        return False

    for arg in arg_list[:6]:
        if not (0 <= arg <= 3):
            return False
    [i1, j1, b1, i2, j2, b2] = arg_list[:6]
    [x, y] = arg_list[6:8]

    if not (-2 <= x <= 2) or not (-2 <= y <= 2):
        return False

    return Move(b1, (i1, j1), b2, (i2,j2), (x,y))

class HumanPlayer:

    def __init__(self, game):
        self.game = game

    def choose_move(self):
        while (True):
            str_move = input("Input your move in this format: i1,j1,b1,i2,j2,b2,x,y\n")
            move = parse_str_move(str_move)
            is_move_valid = True
            if move:
                is_move_valid = self.game.state.validate_move(move)
                if is_move_valid:
                    return move

            print(is_move_valid)
            print('Invalid move. Please choose another move.')

    def make_move(self, move):
        self.game.make_move(move)

    def reset_game(self):
        self.game.reset()

    def __repr__(self):
        return 'Human player'

class RandomPlayer:
    def __init__(self, game):
        self.game = game

    def choose_move(self):
        valid_moves = self.game.state.get_valid_moves()
        move = random.choice(valid_moves)
        return move

    def make_move(self, move):
        self.game.make_move(move)

    def __repr__(self):
        return 'Random player'

class MonteCarloPlayer:
    def __init__(self, game, depth=None, timeout=None):
        self.game = game
        self.timeout = timeout
        self.depth = depth
        self.monte_carlo = MonteCarlo(game)

    def choose_move(self):
        self.monte_carlo.run_search(timeout=self.timeout, max_depth=self.depth)
        move = self.monte_carlo.choose_move()
        self.monte_carlo.reset_tree()
        return move

    def make_move(self, move):
        self.game.make_move(move)

    def __repr__(self):
        return 'Monte Carlo player with max_depth {}.'.format(self.depth)

class MonteCarloEPTPlayer:
    def __init__(self, game, evaluate, depth=None, timeout=None):
        self.game = game
        self.timeout = timeout
        self.depth = depth
        self.evaluate = evaluate
        self.monte_carlo = MonteCarloEPT(game, evaluate)

    def choose_move(self):
        self.monte_carlo.run_search(timeout=self.timeout, max_depth=self.depth)
        move = self.monte_carlo.choose_move()
        self.monte_carlo.reset_tree()
        return move

    def make_move(self, move):
        self.game.make_move(move)

    def __repr__(self):
        return 'Monte Carlo EPT player with max_depth {} and evaluation function {}'.format(self.depth, self.evaluate.__name__)

class MinimaxPlayer:
    def __init__(self, game, depth, breadths, evaluate, tag=None):
        assert depth == len(breadths)
        self.game = game
        self.depth = depth
        self.evaluate = evaluate
        self.tag = tag
        self.minimax = Minimax(game, depth, breadths, evaluate)

    def choose_move(self):
        self.minimax.run_search()
        move = self.minimax.choose_move()
        self.minimax.reset_tree()
        return move

    def make_move(self, move):
        self.game.make_move(move)

    def __repr__(self):
        my_repr=''
        my_repr += 'Minimax Player with depth {} ' \
                   'and evaluation function {}'.format(self.depth, self.evaluate.__name__)
        if self.tag:
            my_repr += ' tag: {}.'.format(self.tag)
        return my_repr

class GreedyPlayer:
    def __init__(self, game):
        self.game = game

    def choose_move(self):
        valid_moves = self.game.state.get_valid_moves()
        for move in valid_moves:
            (captures, _) = self.game.state.does_move_capture(move)
            if captures:
                return move
        return random.choice(valid_moves)

    def make_move(self, move):
        self.game.make_move(move)

    def __repr__(self):
        return 'Greedy player'
