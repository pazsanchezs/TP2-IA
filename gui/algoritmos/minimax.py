import time
from math import inf
from core.game import OthelloGame, BLACK, WHITE

class MinimaxAgent:
    def __init__(self, max_depth=3, player=BLACK):
        self.max_depth = max_depth
        self.player = player
        self.nodes_expanded = 0
        self.name = "MinimaxAgent"

    def evaluate(self, game: OthelloGame):
        black, white = game.count_pieces()
        return black - white if self.player == BLACK else white - black

    def minimax(self, game: OthelloGame, depth: int, maximizing_player: bool):
        self.nodes_expanded += 1

        if depth == 0 or game.is_game_over():
            return self.evaluate(game), None

        current_player = self.player if maximizing_player else game.opponent(self.player)
        valid_moves = game.get_valid_moves(current_player)

        if not valid_moves:
            return self.minimax(game, depth - 1, not maximizing_player)[0], None

        best_value = -inf if maximizing_player else inf
        best_move = None

        for move in valid_moves:
            next_state = game.clone()
            next_state.make_move(*move, current_player)
            value, _ = self.minimax(next_state, depth - 1, not maximizing_player)

            if maximizing_player:
                if value > best_value:
                    best_value = value
                    best_move = move
            else:
                if value < best_value:
                    best_value = value
                    best_move = move

        return best_value, best_move

    def get_move(self, game: OthelloGame):
        self.nodes_expanded = 0
        start_time = time.time()
        _, move = self.minimax(game, self.max_depth, True)
        elapsed_time = time.time() - start_time
        return move, self.nodes_expanded, elapsed_time