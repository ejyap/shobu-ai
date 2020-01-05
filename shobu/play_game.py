from player import HumanPlayer, RandomPlayer, MonteCarloEPTPlayer, MonteCarloPlayer, GreedyPlayer, MinimaxPlayer
from shobu import ShobuGame
from random import randint
from evaluation import stone_advantage, avoid_ones, massive_eval, weighted_value_function, weighted_EPT_value_function
from datetime import datetime


def play_game(game, player1, player2, num_sims=1, max_depth=50, verbose=False):
    results = [0, 0]
    players = [player1, player2]
    for j in range(num_sims):
        i = randint(0, 1)
        print('Starting game {}.'.format(j + 1))
        print('{} starts the game.'.format(players[i]))
        depth = 0
        while not game.state.winner:
            curr_player = players[i]
            if verbose:
                print('{}\'s turn.'.format(curr_player))
            move = curr_player.choose_move()
            curr_player.make_move(move)
            if verbose:
                print(move)
                print(game.state)
            depth += 1
            if depth > max_depth:
                print('------TIE--------')
                break
            i = 0 if i == 1 else 1
        i = 0 if i == 1 else 1
        if depth <= max_depth:
            results[i] += 1
            print('The winner is {}.'.format(players[i]))
            print('The game lasted {} turns.'.format(depth))
        game.reset()
    print('{} won {} out of {} games.'.format(players[i], results[i], num_sims))
    i = 0 if i == 1 else 1
    print('{} won {} out of {} games.'.format(players[i], results[i], num_sims))

game = ShobuGame()
evaluate = weighted_value_function('../weights/smarter_weights_v_greedy1000_218_0.3684210526315789.json')
player1 = GreedyPlayer(game)
player2 = MinimaxPlayer(game, 3, [5, 5, 5], evaluate)

play_game(game, player1, player2, verbose=True)