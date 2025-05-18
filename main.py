from gui.core.game import OthelloGame, BLACK, WHITE
from gui.algoritmos.minimax import MinimaxAgent

# Crear juego y agente
juego = OthelloGame()
agente = MinimaxAgent(max_depth=3, player=BLACK)

# Mostrar tablero inicial
print("Tablero inicial:")
juego.print_board()

# Ejecutar jugadas alternadas hasta que termine el juego o se alcance un número limitado de turnos
turnos = 0
max_turnos = 60

while not juego.is_game_over() and turnos < max_turnos:
    jugador = juego.current_player
    print(f"Turno de {'Negro' if jugador == BLACK else 'Blanco'}")

    if jugador == agente.player:
        movimiento, nodos, tiempo = agente.get_move(juego)
        print(f"Agente elige: {movimiento} (nodos: {nodos}, tiempo: {tiempo:.4f}s)")
    else:
        movimientos = juego.get_valid_moves(jugador)
        movimiento = movimientos[0] if movimientos else None
        print(f"Movimiento automático aleatorio: {movimiento}")

    if movimiento:
        juego.make_move(*movimiento, jugador)
        juego.print_board()
    else:
        print("Sin movimientos válidos. Se pasa el turno.")

    turnos += 1

# Resultado final
negro, blanco = juego.count_pieces()
print(f"\nResultado final -> Negro: {negro}, Blanco: {blanco}")
if negro > blanco:
    print("Gana Negro")
elif blanco > negro:
    print("Gana Blanco")
else:
    print("Empate")