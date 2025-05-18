import time
from math import inf
from core.game import OthelloGame, BLACK, WHITE

class AlphaBetaAgent:
    def __init__(self, max_depth=3, player=BLACK):
        self.max_depth = max_depth
        self.player = player
        self.nodes_expanded = 0
        self.name = "AlphaBethaAgent"

    def evaluate(self, game: OthelloGame):
        black, white = game.count_pieces()
        return black - white if self.player == BLACK else white - black

    def alphabeta(self, game: OthelloGame, depth: int, alpha: float, beta: float, maximizing_player: bool):
        self.nodes_expanded += 1

        if depth == 0 or game.is_game_over():
            return self.evaluate(game), None

        current_player = self.player if maximizing_player else game.opponent(self.player)
        valid_moves = game.get_valid_moves(current_player)

        if not valid_moves:
            return self.alphabeta(game, depth - 1, alpha, beta, not maximizing_player)[0], None

        best_move = None

        if maximizing_player:
            max_eval = -inf
            for move in valid_moves:
                next_state = game.clone()
                next_state.make_move(*move, current_player)
                eval, _ = self.alphabeta(next_state, depth - 1, alpha, beta, False)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move

        else:
            min_eval = inf
            for move in valid_moves:
                next_state = game.clone()
                next_state.make_move(*move, current_player)
                eval, _ = self.alphabeta(next_state, depth - 1, alpha, beta, True)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_move(self, game: OthelloGame):
        self.nodes_expanded = 0
        start_time = time.time()
        _, move = self.alphabeta(game, self.max_depth, -inf, inf, True)
        elapsed_time = time.time() - start_time
        return move, self.nodes_expanded, elapsed_time