import math
import random
from time import time
from collections import defaultdict

class MCTSNode():

    def __init__(self, state, pmove=None, parent=None, bias=math.sqrt(2), depth=0):
        self.state = state #state of the game
        self.pmove = pmove #Move made by the parent to get to this node
        self.parent = parent #Parent Monte Carlo Node
        self.is_fully_expanded = False
        self.unexpanded_moves = None
        self.player = self.state.player
        self.N=0
        self.W= defaultdict(int)
        self.bias = bias
        self.children = {} #Mapping from move to new state
        self.depth = depth

    def winner(self):
        return self.state.check_goal_state()

    def child_node(self, move):
        if move in self.children:
            return self.children[move]
        return None

    def get_unexpanded_moves(self):
        moves = []
        for child in self.children:
            if self.children[child] == None:
                moves.append(child)
        return moves

    def is_leaf(self):
        if len(self.children) == 0:
            return True
        return False

    def select_leaf(self):
        curr = self
        while (curr.is_fully_expanded):
            best_moves = curr.best_child(player=self.player, policy='qu')
            move = random.choice(best_moves)
            if move in self.children:
                curr = self.children[move]
            else:
                return None
        return curr

    def select_leaf(self):
        curr = self
        while (curr.is_fully_expanded):
            best_moves = curr.best_child(player=self.player, policy='qu')
            move = random.choice(best_moves)
            curr = curr.children[move]
        return curr

    def expand(self):
        if self.unexpanded_moves == None:
            self.unexpanded_moves = self.state.get_valid_moves()
        move = self.unexpanded_moves.pop(random.randint(0, len(self.unexpanded_moves)-1))
        if move not in self.children:
            new_state = self.state.make_move(move)
            self.children[move] = MCTSNode(new_state,
                                            pmove=move, parent=self,
                                            bias=self.bias,
                                            depth=self.depth+1)
        if len(self.unexpanded_moves) == 0:
            self.is_fully_expanded = True
        return self.children[move]

    def best_child(self, policy='qu', player=None):

        best_moves = []
        if policy == 'robust':
            max = -1
            for child in self.children.values():
                if child.state.winner == self.state.player:
                    return [child.pmove]
                if child.N > max:
                    best_moves = [child.pmove]
                    max = child.N
                    # print('max child.N = {}.'.format(child.N))
                    # print('max wins = {}'.format(child.W.get(self.player, 0)))
                elif child.N == max:
                    best_moves.append(child.pmove)
        elif policy == 'qu':
            best_UCB1 = -1
            for child in self.children.values():
                child_UCB1 = child.get_UCB1(self.player)
                if child_UCB1 > best_UCB1:
                    best_moves = [child.pmove]
                    best_UCB1 = child_UCB1
                elif child_UCB1 == best_UCB1:
                    best_moves.append(child.pmove)
        return best_moves


    def backpropagate(self, value, player=None):
        if not player:
            player = self.state.winner
        curr = self

        while curr:
            curr.N+=1
            curr.W[player]+=value
            curr=curr.parent


    def get_UCB1(self, player):
        if not self.parent:
            return 0
        W = self.W.get(player,0)
        try:
            ucb = (W/self.N) + (self.bias * math.sqrt(math.log(self.parent.N)/self.N))
        except ZeroDivisionError:
            ucb = float("inf")
        return ucb

    def __repr__(self):
        return 'state=%r move=%r visits=%r wins=%r ucb=%r' % (
            self.state,
            self.pmove if self.pmove else "None",
            self.N,
            self.W.get(self.player, 0),
            self.get_UCB1(self.player))

class MonteCarlo:

    def __init__(self, game, bias=math.sqrt(2)):
        self.game = game
        self.bias = bias
        self.root = None

    def run_search(self, num_reads=1, timeout=0, max_depth=None):

        if max_depth == None:
            max_depth=200
        self.root = MCTSNode(self.game.state, bias=self.bias)
        if timeout > 0:
            num_reads = 10000000000
        start_time = time()
        for i in range(num_reads):
            if timeout and time()-start_time > timeout:
                break
            curr=self.root.select_leaf()

            if not curr:
                continue
            depth = 0
            while curr.state.winner == 0 and depth < max_depth:
                curr = curr.expand()
                depth+=1
            value = 1 if curr.state.winner else 0
            curr.backpropagate(value)
        #print((self.root.N, self.root.W[self.root.player]))
        # print(self.root.N)
        # print(len(self.root.children))
        sum = 0
        for s in list(self.root.children.values()):
            sum+=s.N
        # print('sum={}'.format(sum))
        # print('num of simulations: {}'.format(i))

    def choose_move(self):
        best_moves = self.root.best_child(policy='robust')
        move = random.choice(best_moves)
        return move

    def reset_tree(self):
        self.root=None

class MonteCarloEPT:

    def __init__(self, game, evaluate, bias=math.sqrt(2)):
        self.game = game
        self.bias = bias
        self.root = None
        self.evaluate = evaluate

    def run_search(self, num_reads=1, timeout=0, max_depth=None):
        if max_depth == None:
            max_depth=200
        self.root = MCTSNode(self.game.state, bias=self.bias)
        if timeout > 0:
            num_reads = 10000000000
        start_time = time()
        for i in range(num_reads):
            if timeout and time()-start_time > timeout:
                break
            curr=self.root.select_leaf()
            depth = 0
            while curr.state.winner == 0 and depth < max_depth:
                curr = curr.expand()
                depth+=1
            if curr.state.winner:
                reward = 1
                player=curr.state.winner
            else:
                value = self.evaluate(curr.state, self.root.player)
                reward = 1 if value else 0
                player = self.root.player*-1 if value < 0 else self.root.player

            curr.backpropagate(reward, player=player)
        # print(self.root.N)
        # print(len(self.root.children))
        sum = 0
        for s in list(self.root.children.values()):
            sum+=s.N
        # print('sum={}'.format(sum))
        # print('num of simulations: {}'.format(i))
        #print((self.root.N, self.root.W[self.root.player]))

    def reset_tree(self):
        self.root=None

    def choose_move(self):
        best_moves = self.root.best_child(policy='robust')
        move = random.choice(best_moves)
        return move
