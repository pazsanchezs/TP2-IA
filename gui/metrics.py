import time
from core.game import OthelloGame, BLACK, WHITE
from algoritmos.minimax import MinimaxAgent
from algoritmos.alphabeta import AlphaBetaAgent
from algoritmos.reinforcement import QLearningAgent


def play_game(agent_black, agent_white):
    game = OthelloGame()
    total_times = {BLACK: 0.0, WHITE: 0.0}
    total_nodes = {BLACK: 0, WHITE: 0}

    while not game.is_game_over():
        current = game.current_player
        agent = agent_black if current == BLACK else agent_white

        start = time.time()
        move, nodes, elapsed = agent.get_move(game)
        end = time.time()

        if move:
            game.make_move(*move, current)

        total_times[current] += elapsed if elapsed else (end - start)
        total_nodes[current] += nodes if nodes else 0

    black_score, white_score = game.count_pieces()
    result = {
        "black_score": black_score,
        "white_score": white_score,
        "winner": "BLACK" if black_score > white_score else "WHITE" if white_score > black_score else "DRAW",
        "black_time": round(total_times[BLACK], 3),
        "white_time": round(total_times[WHITE], 3),
        "black_nodes": total_nodes[BLACK],
        "white_nodes": total_nodes[WHITE]
    }
    return result


def run_experiments():
    levels = [2, 3, 4]  # puedes modificar estos niveles según tiempo disponible
    print("| Algoritmo B | Nivel B | Algoritmo W | Nivel W | Winner | B_Time | W_Time | B_Nodes | W_Nodes |")
    print("|-------------|---------|-------------|---------|--------|--------|--------|---------|---------|")

    for level in levels:
        # Minimax vs AlphaBeta
        b_agent = MinimaxAgent(max_depth=level, player=BLACK)
        w_agent = AlphaBetaAgent(max_depth=level, player=WHITE)
        res = play_game(b_agent, w_agent)
        print(f"| Minimax     | {level:<7}| AlphaBeta  | {level:<7}| {res['winner']:<6} | {res['black_time']:<6} | {res['white_time']:<6} | {res['black_nodes']:<7} | {res['white_nodes']:<7} |")

        # AlphaBeta vs QLearning
        b_agent = AlphaBetaAgent(max_depth=level, player=BLACK)
        q_agent = QLearningAgent(player=WHITE)
        try:
            q_agent.load("q_agent.pkl")
        except:
            q_agent.train(500)
            q_agent.save("q_agent.pkl")
        res = play_game(b_agent, q_agent)
        print(f"| AlphaBeta   | {level:<7}| QLearning  | -       | {res['winner']:<6} | {res['black_time']:<6} | {res['white_time']:<6} | {res['black_nodes']:<7} | {res['white_nodes']:<7} |")

        # Minimax vs QLearning
        b_agent = MinimaxAgent(max_depth=level, player=BLACK)
        q_agent = QLearningAgent(player=WHITE)
        try:
            q_agent.load("q_agent.pkl")
        except:
            q_agent.train(500)
            q_agent.save("q_agent.pkl")
        res = play_game(b_agent, q_agent)
        print(f"| Minimax     | {level:<7}| QLearning  | -       | {res['winner']:<6} | {res['black_time']:<6} | {res['white_time']:<6} | {res['black_nodes']:<7} | {res['white_nodes']:<7} |")


if __name__ == "__main__":
    run_experiments()
