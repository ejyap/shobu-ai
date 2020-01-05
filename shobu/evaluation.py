import numpy as np
from shobu import Board, getPosition, checkBounds
import json

def stone_advantage(state, player):
    stone_sum = np.sum(state.get_flattened_board())*player
    return stone_sum

def avoid_ones(state):
    boards_sum = 0
    for board in state.boards:
        one_count = np.count_nonzero(board == 1)
        neg_one_count = np.count_nonzero(board == -1)
        boards_sum -= (4 - one_count) ** 2
        boards_sum += (4 - neg_one_count) ** 2
    return boards_sum

def mobility(moves):
    return len(moves)

def stones_threatened(state, moves):
    stone_count=0
    for move in moves:
        captures, piece = state.does_move_capture(move)
        if captures:
            stone_count+=1
    return stone_count

def unique_stones_threatened(state, moves):
    stone_count=0
    stones_captured = set()
    for move in moves:
        captures, piece = state.does_move_capture(move)
        if captures:
            if (piece, move.second_board) not in stones_captured:
                stones_captured.add((piece, move.second_board))
                stone_count+=1
    return stone_count

def board_diff(board, player):
    one_count = np.count_nonzero(board == 1)
    neg_one_count = np.count_nonzero(board == -1)
    diff = one_count - neg_one_count
    return player*diff

def count_stone_comp(state, num, player):
    num_boards_comp = 0
    for board in state.boards:
        comp_count = np.count_nonzero(board == player)
        if comp_count == num:
            num_boards_comp+=1
    return num_boards_comp

def threatened_ones(state,moves, player):
    stone_count=0
    for move in moves:
        captures, piece = state.does_move_capture(move)
        if captures and np.count_nonzero(state.boards[move.second_board] == player) == 1:
            stone_count+=1
    return stone_count

def defensive_stones(state, player):
    if player == 1:
        board_indices = (2,3)
    else:
        board_indices = (0,1)

    stone_sum = 0
    for i in board_indices:
        stone_sum += np.count_nonzero(state.boards[i]==player)
    return stone_sum

def offensive_stones(state, player):
    if player == 1:
        board_indices = (0, 1)
    else:
        board_indices = (2, 3)

    stone_sum = 0
    for i in board_indices:
        stone_sum += np.count_nonzero(state.boards[i] == player)
    return stone_sum

def active_stones(state, player):
    active_stone_count = 0
    for board in state.boards:
        if player == 1:
            active_stone_count += np.count_nonzero(board[:-4] == player)
        else:
            active_stone_count += np.count_nonzero(board[4:] == player)
    return active_stone_count

def specific_boards_stone_count(state, indices, player):
    stone_sum = 0
    for i in indices:
        stone_sum += np.count_nonzero(state.boards[i] == player)
    return stone_sum

def offensive_front_stone_count(state, player):
    stone_count = 0
    for board in state.boards:
        if player == 1:
            stone_count += np.count_nonzero(board[:-8] == player)
        else:
            stone_count += np.count_nonzero(board[8:] == player)
    return stone_count

def back_stone_count(state, player):
    stone_count = 0
    for board in state.boards:
        if player == 1:
            stone_count += np.count_nonzero(board[8:] == player)
        else:
            stone_count += np.count_nonzero(board[:-8] == player)
    return stone_count

def connected_stones(state, player):
    connected_stones_count = 0
    for board in state.boards:
        for i, piece in enumerate(board.flatten()):
            if piece == player:
                x, y = getPosition(i)
                for _x, _y in [(1,0), (0,1), (-1,0), (0,-1), (1,1), (-1,1), (1,-1), (-1,-1)]:
                    if checkBounds((x+_x, y+_y)) and board[(x+_x, y+_y)]==player:
                        connected_stones_count+=1
    return connected_stones_count


def average_mobility(state, moves, player):
    stone_count = np.count_nonzero(state.get_flattened_board() == player)

    move_count = len(moves)
    return move_count/stone_count

def win(state, player):
    for board in state.boards:
        if np.count_nonzero(board == -player) == 0:
            return 1
    return 0

def massive_eval(state, player):
    boards = state.boards
    moves = state.get_valid_moves(player)
    his_moves = state.get_valid_moves(player*-1)
    eval = {}
    eval['my_stone_count'] = np.count_nonzero(state.get_flattened_board()==player)/16
    eval['his_stone_count'] = np.count_nonzero(state.get_flattened_board()==-player)/16
    eval['my_mobility'] = mobility(moves)/232
    eval['his_mobility'] = mobility(his_moves)/232
    eval['my_stones_threatened'] = stones_threatened(state, his_moves)/16
    eval['his_stones_threatened'] = stones_threatened(state, moves)/16
    eval['my_unique_stones_threatened'] = unique_stones_threatened(state, his_moves)/16
    eval['his_unique_stones_threatened'] = unique_stones_threatened(state, moves)/16
    eval['my_ones'] = count_stone_comp(state, 1, player)/4
    eval['his_ones'] = count_stone_comp(state, 1, -player)/4
    eval['my_twos'] = count_stone_comp(state, 2, player)/4
    eval['his_twos'] = count_stone_comp(state, 2, -player)/4
    eval['my_threes'] = count_stone_comp(state, 3, player)/4
    eval['his_threes'] = count_stone_comp(state, 3, -player)/4
    eval['my_fours'] = count_stone_comp(state, 4, player)/4
    eval['his_fours'] = count_stone_comp(state, 4, -player)/4
    eval['my_threatened_ones'] = threatened_ones(state, his_moves, player)/4
    eval['his_threatened_ones'] = threatened_ones(state, moves, -player)/4
    eval['my_defensive_stones'] = defensive_stones(state, player)/8
    eval['his_defensive_stones'] = defensive_stones(state, -player)/8
    eval['my_offensive_stones'] = offensive_stones(state, player)/8
    eval['his_offensive_stones'] = offensive_stones(state, -player)/8
    eval['my_unthreatened_stones'] = eval['my_stone_count'] - eval['my_unique_stones_threatened']
    eval['his_unthreatened_stones'] = eval['his_stone_count'] - eval['his_unique_stones_threatened']
    eval['my_active_stones'] = active_stones(state, player)/16
    eval['his_active_stones'] = active_stones(state, -player)/16
    eval['my_diagonal_stone_count1'] = specific_boards_stone_count(state, (1,3), player)/8
    eval['my_diagonal_stone_count2'] = specific_boards_stone_count(state, (0,2), player)/8
    eval['his_diagonal_stone_count1'] = specific_boards_stone_count(state, (1, 3), -player)/8
    eval['his_diagonal_stone_count2'] = specific_boards_stone_count(state, (0, 2), -player)/8
    eval['my_offensive_front_stone_count'] = offensive_front_stone_count(state, player)/16
    eval['his_offensive_front_stone_count'] = offensive_front_stone_count(state, -player)/16
    eval['my_back_stone_count'] = back_stone_count(state, player)/16
    eval['his_back_stone_count'] = back_stone_count(state, -player) / 16
    eval['my_vertical_stone_count1'] = specific_boards_stone_count(state, (0,2), player)/8
    eval['my_vertical_stone_count2'] = specific_boards_stone_count(state, (1,3), player)/8
    eval['his_vertical_stone_count1'] = specific_boards_stone_count(state, (0,2), -player)/8
    eval['his_vertical_stone_count2'] = specific_boards_stone_count(state, (1,3), -player)/8
    eval['my_connected_stones'] = connected_stones(state, player)/24
    eval['his_connected_stones'] = connected_stones(state, -player)/24
    eval['my_average_mobility'] = average_mobility(state, moves, player)/14.5
    eval['his_average_mobility'] = average_mobility(state, his_moves, -player)/14.
    eval['my_average_threatening'] = eval['his_stones_threatened']/eval['my_stone_count']/16
    eval['his_average_threatening'] = eval['my_stones_threatened']/eval['his_stone_count']/16
    eval['diff_stone_count'] = eval['my_stone_count'] - eval['his_stone_count']
    eval['diff_mobility'] = eval['my_mobility'] - eval['his_mobility']
    eval['diff_threatened'] = eval['his_stones_threatened'] - eval['my_stones_threatened']
    eval['diff_unique_threatened'] = eval['his_unique_stones_threatened'] - eval['my_unique_stones_threatened']

    return eval

def weighted_value_function(weights_file):
    with open(weights_file, 'r') as JSON:
        weights = json.load(JSON)

    def custom_value_function(state, player):
        value = 0
        moves = state.get_valid_moves(player)
        his_moves = state.get_valid_moves(player * -1)
        features = {}
        features['my_stone_count'] = np.count_nonzero(state.get_flattened_board() == player) / 16
        features['his_stone_count'] = np.count_nonzero(state.get_flattened_board() == -player) / 16
        features['my_mobility'] = mobility(moves) / 232
        features['his_mobility'] = mobility(his_moves) / 232
        features['my_stones_threatened'] = stones_threatened(state, his_moves) / 16
        features['his_stones_threatened'] = stones_threatened(state, moves) / 16
        features['my_unique_stones_threatened'] = unique_stones_threatened(state, his_moves) / 16
        features['his_unique_stones_threatened'] = unique_stones_threatened(state, moves) / 16
        features['my_ones'] = count_stone_comp(state, 1, player) / 4
        features['his_ones'] = count_stone_comp(state, 1, -player) / 4
        features['my_twos'] = count_stone_comp(state, 2, player) / 4
        features['his_twos'] = count_stone_comp(state, 2, -player) / 4
        features['my_threes'] = count_stone_comp(state, 3, player) / 4
        features['his_threes'] = count_stone_comp(state, 3, -player) / 4
        features['my_fours'] = count_stone_comp(state, 4, player) / 4
        features['his_fours'] = count_stone_comp(state, 4, -player) / 4
        features['my_threatened_ones'] = threatened_ones(state, his_moves, player) / 4
        features['his_threatened_ones'] = threatened_ones(state, moves, -player) / 4
        features['my_defensive_stones'] = defensive_stones(state, player) / 8
        features['his_defensive_stones'] = defensive_stones(state, -player) / 8
        features['my_offensive_stones'] = offensive_stones(state, player) / 8
        features['his_offensive_stones'] = offensive_stones(state, -player) / 8
        features['my_unthreatened_stones'] = features['my_stone_count'] - features['my_unique_stones_threatened']
        features['his_unthreatened_stones'] = features['his_stone_count'] - features['his_unique_stones_threatened']
        features['my_active_stones'] = active_stones(state, player) / 16
        features['his_active_stones'] = active_stones(state, -player) / 16
        features['my_diagonal_stone_count1'] = specific_boards_stone_count(state, (1, 3), player) / 8
        features['my_diagonal_stone_count2'] = specific_boards_stone_count(state, (0, 2), player) / 8
        features['his_diagonal_stone_count1'] = specific_boards_stone_count(state, (1, 3), -player) / 8
        features['his_diagonal_stone_count2'] = specific_boards_stone_count(state, (0, 2), -player) / 8
        features['my_offensive_front_stone_count'] = offensive_front_stone_count(state, player) / 16
        features['his_offensive_front_stone_count'] = offensive_front_stone_count(state, -player) / 16
        features['my_back_stone_count'] = back_stone_count(state, player) / 16
        features['his_back_stone_count'] = back_stone_count(state, -player) / 16
        features['my_vertical_stone_count1'] = specific_boards_stone_count(state, (0, 2), player) / 8
        features['my_vertical_stone_count2'] = specific_boards_stone_count(state, (1, 3), player) / 8
        features['his_vertical_stone_count1'] = specific_boards_stone_count(state, (0, 2), -player) / 8
        features['his_vertical_stone_count2'] = specific_boards_stone_count(state, (1, 3), -player) / 8
        features['my_connected_stones'] = connected_stones(state, player) / 24
        features['his_connected_stones'] = connected_stones(state, -player) / 24
        features['my_average_mobility'] = average_mobility(state, moves, player) / 14.5
        features['his_average_mobility'] = average_mobility(state, his_moves, -player) / 14.
        features['my_average_threatening'] = features['his_stones_threatened'] / features['my_stone_count'] / 16
        features['his_average_threatening'] = features['my_stones_threatened'] / features['his_stone_count'] / 16
        features['diff_stone_count'] = features['my_stone_count'] - features['his_stone_count']
        features['diff_mobility'] = features['my_mobility'] - features['his_mobility']
        features['diff_threatened'] = features['his_stones_threatened'] - features['my_stones_threatened']
        features['diff_unique_threatened'] = features['his_unique_stones_threatened'] - features['my_unique_stones_threatened']
        for feature in features.keys():
            value+=features[feature]*weights[feature]
        value+=100000*win(state, player)
        value+=-100000*win(state, -player)
        return value
    return custom_value_function

def weighted_EPT_value_function(weights_file, threshold):
    with open(weights_file, 'r') as JSON:
        weights = json.load(JSON)

    def custom_value_function(state, player):
        value = 0
        moves = state.get_valid_moves(player)
        his_moves = state.get_valid_moves(player * -1)
        features = {}
        features['my_stone_count'] = np.count_nonzero(state.get_flattened_board() == player) / 16
        features['his_stone_count'] = np.count_nonzero(state.get_flattened_board() == -player) / 16
        features['my_mobility'] = mobility(moves) / 232
        features['his_mobility'] = mobility(his_moves) / 232
        features['my_stones_threatened'] = stones_threatened(state, his_moves) / 16
        features['his_stones_threatened'] = stones_threatened(state, moves) / 16
        features['my_unique_stones_threatened'] = unique_stones_threatened(state, his_moves) / 16
        features['his_unique_stones_threatened'] = unique_stones_threatened(state, moves) / 16
        features['my_ones'] = count_stone_comp(state, 1, player) / 4
        features['his_ones'] = count_stone_comp(state, 1, -player) / 4
        features['my_twos'] = count_stone_comp(state, 2, player) / 4
        features['his_twos'] = count_stone_comp(state, 2, -player) / 4
        features['my_threes'] = count_stone_comp(state, 3, player) / 4
        features['his_threes'] = count_stone_comp(state, 3, -player) / 4
        features['my_fours'] = count_stone_comp(state, 4, player) / 4
        features['his_fours'] = count_stone_comp(state, 4, -player) / 4
        features['my_threatened_ones'] = threatened_ones(state, his_moves, player) / 4
        features['his_threatened_ones'] = threatened_ones(state, moves, -player) / 4
        features['my_defensive_stones'] = defensive_stones(state, player) / 8
        features['his_defensive_stones'] = defensive_stones(state, -player) / 8
        features['my_offensive_stones'] = offensive_stones(state, player) / 8
        features['his_offensive_stones'] = offensive_stones(state, -player) / 8
        features['my_unthreatened_stones'] = features['my_stone_count'] - features['my_unique_stones_threatened']
        features['his_unthreatened_stones'] = features['his_stone_count'] - features['his_unique_stones_threatened']
        features['my_active_stones'] = active_stones(state, player) / 16
        features['his_active_stones'] = active_stones(state, -player) / 16
        features['my_diagonal_stone_count1'] = specific_boards_stone_count(state, (1, 3), player) / 8
        features['my_diagonal_stone_count2'] = specific_boards_stone_count(state, (0, 2), player) / 8
        features['his_diagonal_stone_count1'] = specific_boards_stone_count(state, (1, 3), -player) / 8
        features['his_diagonal_stone_count2'] = specific_boards_stone_count(state, (0, 2), -player) / 8
        features['my_offensive_front_stone_count'] = offensive_front_stone_count(state, player) / 16
        features['his_offensive_front_stone_count'] = offensive_front_stone_count(state, -player) / 16
        features['my_back_stone_count'] = back_stone_count(state, player) / 16
        features['his_back_stone_count'] = back_stone_count(state, -player) / 16
        features['my_vertical_stone_count1'] = specific_boards_stone_count(state, (0, 2), player) / 8
        features['my_vertical_stone_count2'] = specific_boards_stone_count(state, (1, 3), player) / 8
        features['his_vertical_stone_count1'] = specific_boards_stone_count(state, (0, 2), -player) / 8
        features['his_vertical_stone_count2'] = specific_boards_stone_count(state, (1, 3), -player) / 8
        features['my_connected_stones'] = connected_stones(state, player) / 24
        features['his_connected_stones'] = connected_stones(state, -player) / 24
        features['my_average_mobility'] = average_mobility(state, moves, player) / 14.5
        features['his_average_mobility'] = average_mobility(state, his_moves, -player) / 14.
        features['my_average_threatening'] = features['his_stones_threatened'] / features['my_stone_count'] / 16
        features['his_average_threatening'] = features['my_stones_threatened'] / features['his_stone_count'] / 16
        features['diff_stone_count'] = features['my_stone_count'] - features['his_stone_count']
        features['diff_mobility'] = features['my_mobility'] - features['his_mobility']
        features['diff_threatened'] = features['his_stones_threatened'] - features['my_stones_threatened']
        features['diff_unique_threatened'] = features['his_unique_stones_threatened'] - features['my_unique_stones_threatened']
        for feature in features.keys():
            value+=features[feature]*weights[feature]
        value+=100000*win(state, player)
        value += -100000 * win(state, -player)
        if value > threshold:
            return 1
        elif value < threshold:
            return -1
        return 0
    return custom_value_function