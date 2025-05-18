import time
import random
import pickle
from collections import defaultdict
from core.game import OthelloGame, BLACK, WHITE

class QLearningAgent:
    def __init__(self, player=BLACK, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.player = player
        self.alpha = alpha    
        self.gamma = gamma     
        self.epsilon = epsilon  
        self.q_table = defaultdict(float)
        self.name = "RLAgent"

    def get_state_key(self, game):
        return ''.join([''.join(row) for row in game.board]) + game.current_player

    def get_valid_actions(self, game):
        return game.get_valid_moves(self.player)

    def choose_action(self, game):
        state = self.get_state_key(game)
        actions = self.get_valid_actions(game)

        if not actions:
            return None

        if random.random() < self.epsilon:
            return random.choice(actions)

        q_values = [self.q_table[(state, action)] for action in actions]
        max_q = max(q_values)
        best_actions = [a for a, q in zip(actions, q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, old_game, action, reward, new_game):
        old_state = self.get_state_key(old_game)
        new_state = self.get_state_key(new_game)
        future_qs = [self.q_table[(new_state, a)] for a in self.get_valid_actions(new_game)]
        max_future_q = max(future_qs, default=0.0)

        old_q = self.q_table[(old_state, action)]
        self.q_table[(old_state, action)] = old_q + self.alpha * (reward + self.gamma * max_future_q - old_q)

    def train(self, episodes=1000, log_file="training_log.txt"):
        with open(log_file, 'w') as f:  #para mostrar el entrenamiento del agente
            for ep in range(episodes):
                game = OthelloGame()
                f.write(f"=== Episodio {ep+1} ===\n")
                while not game.is_game_over():
                    state = game.clone()
                    if game.current_player == self.player:
                        action = self.choose_action(game)
                        if action:
                            game.make_move(*action, self.player)
                            reward = self.get_reward(game)
                            self.learn(state, action, reward, game)
                            f.write(f"Jugador RL ({self.player}) hizo movimiento: {action}\n")
                        else:
                            f.write("Jugador RL sin movimientos válidos\n")
                            break
                    else:
                        enemy_moves = game.get_valid_moves(game.current_player)
                        if enemy_moves:
                            move = random.choice(enemy_moves)
                            game.make_move(*move, game.current_player)
                            f.write(f"Jugador rival ({game.current_player}) hizo movimiento: {move}\n")
                        else:
                            f.write(f"Jugador rival ({game.current_player}) sin movimientos válidos\n")
                            break
                black, white = game.count_pieces()
                f.write(f"Resultado final: BLACK={black}, WHITE={white}\n\n")

    def get_reward(self, game):
        black, white = game.count_pieces()
        if game.is_game_over():
            if self.player == BLACK:
                return 1 if black > white else -1 if white > black else 0
            else:
                return 1 if white > black else -1 if black > white else 0
        return 0

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.q_table = defaultdict(float, pickle.load(f))


    def get_move(self, game):
        self.nodes_expanded = 0
        start = time.perf_counter()
        action = self.choose_action(game)
        end = time.perf_counter()
        elapsed = end - start
        return action,self.nodes_expanded, elapsed

