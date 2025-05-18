import tkinter as tk
from tkinter import ttk, messagebox
from core.game import OthelloGame, BLACK, WHITE
from algoritmos.minimax import MinimaxAgent
from algoritmos.humano import HumanoAgent
from algoritmos.alphabeta import AlphaBetaAgent
from algoritmos.reinforcement import QLearningAgent
import time
import os

class OthelloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Othello")
        self.board_buttons = [[None for _ in range(8)] for _ in range(8)]
        self.game = OthelloGame()
        self.metrics_tree = None

        self.black_player_type = tk.StringVar(value="Humano")
        self.white_player_type = tk.StringVar(value="Humano")
        self.depth_black = tk.IntVar(value=0)
        self.depth_white = tk.IntVar(value=0)
        self.agents = {BLACK: None, WHITE: None}
        self.q_agent_file = "q_agent.pkl"

        self._setup_ui()
        self.update_board()

        self.black_agent = self.create_agent(BLACK)
        self.white_agent = self.create_agent(WHITE)
        self.agents = {BLACK: self.black_agent, WHITE: self.white_agent}
        self.stats = {
            BLACK: {"time": 0.0, "nodes": 0},
            WHITE: {"time": 0.0, "nodes": 0}
        }

    def reset_game(self):
        self.game = OthelloGame()
        self.reset_stats()
        self.black_agent = self.create_agent(BLACK)
        self.white_agent = self.create_agent(WHITE)
        self.agents = {BLACK: self.black_agent, WHITE: self.white_agent}
        self.info_label.config(text="")
        if self.metrics_tree:
            for row in self.metrics_tree.get_children():
                self.metrics_tree.delete(row)
        self.update_board()

    def reset_stats(self):
        self.stats = {
            BLACK: {"time": 0.0, "nodes": 0},
            WHITE: {"time": 0.0, "nodes": 0}
        }


    def _setup_ui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10)

        ttk.Label(top_frame, text="Jugador Negro:").grid(row=0, column=0)
        black_player_menu = ttk.Combobox(top_frame, textvariable=self.black_player_type,
                                         values=["Humano", "Minimax", "AlphaBeta", "RL"], width=12)
        black_player_menu.grid(row=0, column=1)
        black_player_menu.bind("<<ComboboxSelected>>", lambda e: self._update_depth_state(BLACK))

        ttk.Label(top_frame, text="Nivel Negro (N):").grid(row=0, column=2)
        self.depth_black_entry = ttk.Entry(top_frame, textvariable=self.depth_black, width=5)
        self.depth_black_entry.grid(row=0, column=3)

        ttk.Label(top_frame, text="Jugador Blanco:").grid(row=1, column=0)
        white_player_menu = ttk.Combobox(top_frame, textvariable=self.white_player_type,
                                         values=["Humano", "Minimax", "AlphaBeta", "RL"], width=12)
        white_player_menu.grid(row=1, column=1)
        white_player_menu.bind("<<ComboboxSelected>>", lambda e: self._update_depth_state(WHITE))

        ttk.Label(top_frame, text="Nivel Blanco (N):").grid(row=1, column=2)
        self.depth_white_entry = ttk.Entry(top_frame, textvariable=self.depth_white, width=5)
        self.depth_white_entry.grid(row=1, column=3)

        ttk.Button(top_frame, text="Empezar", command=self.reset_game).grid(row=0, column=4, rowspan=2, padx=10)

        self.info_label = ttk.Label(self.root, text="")
        self.info_label.pack(pady=5)

        # Tablero
        board_frame = ttk.Frame(self.root)
        board_frame.pack()
        for i in range(8):
            for j in range(8):
                btn = tk.Button(board_frame, width=4, height=2, bg="green",
                                command=lambda x=i, y=j: self.player_move(x, y))
                btn.grid(row=i, column=j)
                self.board_buttons[i][j] = btn

        # Tabla de métricas
        self.metrics_tree = ttk.Treeview(self.root, columns=("Jugador", "Algoritmo", "Tiempo", "Nodos"), show="headings", height=2)
        self.metrics_tree.heading("Jugador", text="Jugador")
        self.metrics_tree.heading("Algoritmo", text="Algoritmo")
        self.metrics_tree.heading("Tiempo", text="Tiempo (s)")
        self.metrics_tree.heading("Nodos", text="Nodos")
        self.metrics_tree.pack(pady=10)

        self._update_depth_state(BLACK)
        self._update_depth_state(WHITE)

    def _update_depth_state(self, player):
        tipo = self.black_player_type.get() if player == BLACK else self.white_player_type.get()
        entry = self.depth_black_entry if player == BLACK else self.depth_white_entry
        entry.config(state="normal" if tipo in ["Minimax", "AlphaBeta"] else "disabled")

    def update_board(self):
        for i in range(8):
            for j in range(8):
                val = self.game.board[i][j]
                btn = self.board_buttons[i][j]
                if val == BLACK:
                    btn.config(text="B", bg="black", fg="white")
                elif val == WHITE:
                    btn.config(text="W", bg="white", fg="black")
                else:
                    btn.config(text="", bg="green")

        if self.game.is_game_over():
            self.show_final_metrics()
        else:
            current = self.game.current_player
            if self.agents[current]:
                self.root.after(500, self.agent_move)

    def player_move(self, x, y):
        current = self.game.current_player
        if (current == BLACK and self.black_player_type.get() != "Humano") or \
           (current == WHITE and self.white_player_type.get() != "Humano"):
            return
        if self.game.make_move(x, y, current):
            self.update_board()

    def agent_move(self):
        current = self.game.current_player

        if not hasattr(self, "stats"):
            self.reset_stats()
            self.stats = {
                BLACK: {"time": 0.0, "nodes": 0},
                WHITE: {"time": 0.0, "nodes": 0}
            }

        valid_moves_current = self.game.get_valid_moves(current)
        opponent = BLACK if current == WHITE else WHITE
        valid_moves_opponent = self.game.get_valid_moves(opponent)

        if not valid_moves_current:
            if not valid_moves_opponent:
                self.show_final_metrics()
                return
            else:
                self.game.current_player = opponent
                self.root.after(500, self.agent_move)
                return

        start_time = time.time()
        if current == BLACK:
            move, nodes, _ = self.black_agent.get_move(self.game)
        else:
            move, nodes, _ = self.white_agent.get_move(self.game)
        elapsed = time.time() - start_time

        self.stats[current]["time"] += elapsed
        self.stats[current]["nodes"] += nodes

        if move:
            self.game.make_move(*move, current)
        self.update_board()

    def show_final_metrics(self):
        black, white = self.game.count_pieces()
        result = f"Juego terminado - Negras: {black} | Blancas: {white}"
        self.info_label.config(text=result)

        for row in self.metrics_tree.get_children():
            self.metrics_tree.delete(row)

        for player, name in [(BLACK, "Negras"), (WHITE, "Blancas")]:
            agent = self.black_agent if player == BLACK else self.white_agent
            alg = agent.name if agent else "Humano"
            tiempo = self.stats[player]["time"] if hasattr(self, "stats") else 0
            nodos = self.stats[player]["nodes"] if hasattr(self, "stats") else 0
            self.metrics_tree.insert("", "end", values=(name, alg, f"{tiempo:.2f}", nodos))

    def create_agent(self, player):
        tipo = self.black_player_type.get() if player == BLACK else self.white_player_type.get()
        depth = self.depth_black.get() if player == BLACK else self.depth_white.get()

        if tipo == "Minimax":
            return MinimaxAgent(depth, player)
        elif tipo == "AlphaBeta":
            return AlphaBetaAgent(depth, player)
        elif tipo == "RL":
            agent = QLearningAgent(player)
            if os.path.exists(self.q_agent_file):
                agent.load(self.q_agent_file)
            return agent
        else:
            return None
if __name__ == "__main__":
    root = tk.Tk()
    app = OthelloGUI(root)
    root.mainloop()