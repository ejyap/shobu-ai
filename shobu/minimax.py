import random


class MinimaxNode:

    def __init__(self, state, pmove=None, parent=None):
        self.state = state
        self.pmove = pmove
        self.parent = parent
        self.children = {}

    def expand_top_neighbor_states(self, count, evaluate):
        moves = self.state.get_valid_moves()
        results = []
        for move in moves:
            new_state = self.state.make_move(move)
            value = evaluate(new_state, self.state.player)
            results.append((value, new_state, move))
        random.shuffle(results)
        results = sorted(results, reverse=True, key=lambda x: x[0])
        for result in results[:count]:
            value, state, move = result
            self.children[move] = MinimaxNode(state, move, self)

    def get_best_child(self):
        max_value = -float('inf')
        best_move = None
        for child in self.children.values():
            if child.state.winner == self.state.player:
                return child.pmove
            if max_value < child.value:
                max_value = child.value
                best_move = child.pmove
        return best_move

class Minimax:

    def __init__(self, game, depth, breadths, evaluate):
        assert len(breadths) == depth
        self.game = game
        self.depth = depth
        self.breadths = breadths #branching factor at each depth
        self.evaluate = evaluate #evaluation function
        self.root = None

    def reset_tree(self):
        self.root=None

    def run_search(self):
        self.root = MinimaxNode(self.game.state)
        self.minimax(self.root, self.depth, self.breadths, True)

    def minimax(self, node, depth, breadths, maximizingPlayer, alpha=-float('inf'), beta=float('inf')):

        if depth == 0 or node.state.winner:

            node.value = self.evaluate(node.state, self.root.state.player)
            return node.value

        node.expand_top_neighbor_states(breadths[0], self.evaluate)

        if maximizingPlayer:
            value = -float('inf')
            for child in node.children.values():
                value = max(value, self.minimax(child, depth-1, breadths[1:], False, alpha, beta))
                if value >= beta:
                    break
                alpha = max(alpha, value)
            node.value=value
            return value
        else:
            value = float('inf')
            for child in node.children.values():
                value = min(value, self.minimax(child, depth-1, breadths[1:], True, alpha, beta))
                if value <= alpha:
                    break
                beta=min(beta, value)
            node.value = value
            return value

    def choose_move(self):
        return self.root.get_best_child()