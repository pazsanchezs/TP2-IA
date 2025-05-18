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
        self.root.title("Othello AI")
        self.board_buttons = [[None for _ in range(8)] for _ in range(8)]
        self.game = OthelloGame()
        self.metrics_tree = None

        self.black_player_type = tk.StringVar(value="Humano")
        self.white_player_type = tk.StringVar(value="Humano")
        self.depth_black = tk.IntVar(value=0)
        self.depth_white = tk.IntVar(value=0)
        #self.info_label = None
        self.agents = {BLACK: None, WHITE: None}
        self.q_agent_file = "q_agent.pkl"

        self._setup_ui()
        self.update_board()

        # Crear agentes al iniciar
        self.black_agent = self.create_agent(BLACK)
        self.white_agent = self.create_agent(WHITE)
        self.agents = {BLACK: self.black_agent, WHITE: self.white_agent}

    def reset_game(self):
        self.game = OthelloGame()
        # Crear agentes al reiniciar
        self.black_agent = self.create_agent(BLACK)
        self.white_agent = self.create_agent(WHITE)
        self.agents = {BLACK: self.black_agent, WHITE: self.white_agent}
        self.info_label.config(text="")
        self.update_board()

    def _setup_ui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10)

        # Jugador Negro
        ttk.Label(top_frame, text="Jugador Negro:").grid(row=0, column=0, padx=5)
        black_player_menu = ttk.Combobox(top_frame, textvariable=self.black_player_type,
                                        values=["Humano", "Minimax", "AlphaBeta", "RL"], width=12)
        black_player_menu.grid(row=0, column=1, padx=5)
        black_player_menu.bind("<<ComboboxSelected>>", lambda e: self._update_depth_state(BLACK))

        ttk.Label(top_frame, text="Nivel Negro (N):").grid(row=0, column=2, padx=5)
        self.depth_black_entry = ttk.Entry(top_frame, textvariable=self.depth_black, width=5)
        self.depth_black_entry.grid(row=0, column=3, padx=5)

        # Jugador Blanco
        ttk.Label(top_frame, text="Jugador Blanco:").grid(row=1, column=0, padx=5)
        white_player_menu = ttk.Combobox(top_frame, textvariable=self.white_player_type,
                                         values=["Humano", "Minimax", "AlphaBeta", "RL"], width=12)
        white_player_menu.grid(row=1, column=1, padx=5)
        white_player_menu.bind("<<ComboboxSelected>>", lambda e: self._update_depth_state(WHITE))

        ttk.Label(top_frame, text="Nivel Blanco (N):").grid(row=1, column=2, padx=5)
        self.depth_white_entry = ttk.Entry(top_frame, textvariable=self.depth_white, width=5)
        self.depth_white_entry.grid(row=1, column=3, padx=5)

        # Botón Reiniciar
        ttk.Button(top_frame, text="Empezar", command=self.reset_game).grid(row=0, column=4, rowspan=2, padx=10)

        self.info_label = ttk.Label(self.root, text="")
        self.info_label.pack(pady=5)

        board_frame = ttk.Frame(self.root)
        board_frame.pack()
        for i in range(8):
            for j in range(8):
                btn = tk.Button(board_frame, width=4, height=2, bg="green",
                                command=lambda x=i, y=j: self.player_move(x, y))
                btn.grid(row=i, column=j)
                self.board_buttons[i][j] = btn

        self._update_depth_state(BLACK)
        self._update_depth_state(WHITE)

    def _update_depth_state(self, player):
        if player == BLACK:
            tipo = self.black_player_type.get()
            self.depth_black_entry.config(state="normal" if tipo in ["Minimax", "AlphaBeta"] else "disabled")
        else:
            tipo = self.white_player_type.get()
            self.depth_white_entry.config(state="normal" if tipo in ["Minimax", "AlphaBeta"] else "disabled")

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
            black, white = self.game.count_pieces()
            result = f"Juego terminado - Negras: {black} | Blancas: {white}"
            self.info_label.config(text=result)
            return

        current = self.game.current_player
        if self.agents[current]:
            self.root.after(500, self.agent_move)
        elif (self.black_player_type.get() != "Humano" or self.white_player_type.get() != "Humano") and \
            (current == BLACK and self.black_player_type.get() != "Humano") or \
            (current == WHITE and self.white_player_type.get() != "Humano"):
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

    # Inicializar acumuladores si no existen
        if not hasattr(self, "stats"):
            self.stats = {
                BLACK: {"time": 0.0, "nodes": 0},
                WHITE: {"time": 0.0, "nodes": 0}
            }

        valid_moves_current = self.game.get_valid_moves(current)
        opponent = BLACK if current == WHITE else WHITE
        valid_moves_opponent = self.game.get_valid_moves(opponent)

        if not valid_moves_current:
        # No hay movimientos para jugador actual
            if not valid_moves_opponent:
            # Ningún jugador puede mover -> fin del juego
                black_score, white_score = self.game.count_pieces()

                tabla = "\nMÉTRICAS FINALES\n"
                tabla += "-" * 65 + "\n"
                tabla += f"{'Jugador':<10} | {'Algoritmo':<15} | {'Tiempo (s)':<10} | {'Nodos':<10}\n"
                tabla += "-" * 65 + "\n"

                for player, name in [(BLACK, "Negras"), (WHITE, "Blancas")]:
                    agent = self.black_agent if player == BLACK else self.white_agent
                    alg = agent.name if agent else "Humano"
                    tiempo = self.stats[player]["time"]
                    nodos = self.stats[player]["nodes"]
                    tabla += f"{name:<10} | {alg:<15} | {tiempo:<10.2f} | {nodos:<10}\n"

                tabla += "-" * 65 + "\n"
                resultado = f"\nJuego terminado - Negras: {black_score} | Blancas: {white_score}\n"
                self.info_label.config(text=resultado + tabla)
                return
            else:
            # Pasar turno al oponente y llamar agent_move después
                self.game.current_player = opponent
                self.root.after(500, self.agent_move)
                return

    # Si hay movimientos válidos para el jugador actual, hacer movimiento
        start_time = time.time()
        if current == BLACK:
            move, nodes, elapsed_time = self.black_agent.get_move(self.game)
        else:
            move, nodes, elapsed_time = self.white_agent.get_move(self.game)
        end_time = time.time()

        elapsed = end_time - start_time

    # Acumular métricas
        self.stats[current]["time"] += elapsed
        self.stats[current]["nodes"] += nodes

        if move:
            self.game.make_move(*move, current)
        self.update_board()

    # Repetir turno automático si siguiente jugador es agente
        if not self.game.is_game_over():
            self.root.after(500, self.agent_move)
        else:
        # Juego terminó
            black_score, white_score = self.game.count_pieces()

            tabla = "\nMÉTRICAS FINALES\n"
            tabla += "-" * 65 + "\n"
            tabla += f"{'Jugador':<10} | {'Algoritmo':<15} | {'Tiempo (s)':<10} | {'Nodos':<10} | {'Óptimo'}\n"
            tabla += "-" * 65 + "\n"

            for player, name in [(BLACK, "Negras"), (WHITE, "Blancas")]:
                agent = self.black_agent if player == BLACK else self.white_agent
                alg = agent.name if agent else "Humano"
                tiempo = self.stats[player]["time"]
                nodos = self.stats[player]["nodes"]
                tabla += f"{name:<10} | {alg:<15} | {tiempo:<10.2f} | {nodos:<10}\n"

            tabla += "-" * 65 + "\n"
            resultado = f"\nJuego terminado - Negras: {black_score} | Blancas: {white_score}\n"
            self.info_label.config(text=resultado + tabla)

    def create_agent(self, player):
        if player == BLACK:
            tipo = self.black_player_type.get()
            depth = self.depth_black.get()
        else:
            tipo = self.white_player_type.get()
            depth = self.depth_white.get()

        if tipo == "Minimax":
            return MinimaxAgent(depth, player)
        elif tipo == "AlphaBeta":
            return AlphaBetaAgent(depth, player)
        elif tipo == "RL":
            agent = QLearningAgent(player)
            if os.path.exists(self.q_agent_file):
                agent.load(self.q_agent_file)
            else:
                messagebox.showinfo("Entrenando QLearning...", "Entrenando agente por refuerzo (esto puede tardar unos segundos)...")
                agent.train(500)
                agent.save(self.q_agent_file)
            return agent
        elif tipo == "Humano":
            return HumanoAgent(player)
        else:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = OthelloGUI(root)
    root.mainloop()