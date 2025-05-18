from copy import deepcopy

EMPTY = '.'
BLACK = 'B'
WHITE = 'W'

DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),          (0, 1),
    (1, -1),  (1, 0), (1, 1)
]

class OthelloGame:
    def __init__(self):
        self.board = self._initialize_board()
        self.current_player = BLACK

    def _initialize_board(self):
        board = [[EMPTY for _ in range(8)] for _ in range(8)]
        board[3][3], board[4][4] = WHITE, WHITE
        board[3][4], board[4][3] = BLACK, BLACK
        return board

    def in_bounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def opponent(self, player):
        return BLACK if player == WHITE else WHITE

    def is_valid_move(self, x, y, player):
        if not self.in_bounds(x, y) or self.board[x][y] != EMPTY:
            return False

        opponent = self.opponent(player)
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            has_opponent_between = False

            while self.in_bounds(nx, ny) and self.board[nx][ny] == opponent:
                nx += dx
                ny += dy
                has_opponent_between = True

            if has_opponent_between and self.in_bounds(nx, ny) and self.board[nx][ny] == player:
                return True

        return False

    def get_valid_moves(self, player):
        return [(x, y) for x in range(8) for y in range(8) if self.is_valid_move(x, y, player)]

    def make_move(self, x, y, player):
        if not self.is_valid_move(x, y, player):
            return False

        self.board[x][y] = player
        opponent = self.opponent(player)

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            to_flip = []

            while self.in_bounds(nx, ny) and self.board[nx][ny] == opponent:
                to_flip.append((nx, ny))
                nx += dx
                ny += dy

            if self.in_bounds(nx, ny) and self.board[nx][ny] == player:
                for fx, fy in to_flip:
                    self.board[fx][fy] = player

        self.current_player = self.opponent(player)
        return True

    def is_game_over(self):
        return not self.get_valid_moves(BLACK) and not self.get_valid_moves(WHITE)

    def count_pieces(self):
        black = sum(row.count(BLACK) for row in self.board)
        white = sum(row.count(WHITE) for row in self.board)
        return black, white

    def clone(self):
        clone_game = OthelloGame()
        clone_game.board = deepcopy(self.board)
        clone_game.current_player = self.current_player
        return clone_game

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()
