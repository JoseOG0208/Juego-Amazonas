import tkinter as tk
from tkinter import messagebox
import random

# tamaño del tablero y casillas
TILE_SIZE = 60
BOARD_SIZE = 10

# posiciones de inicio para cada jugador
START_POSITIONS = {
    "white": [(0, 3), (0, 6), (3, 0), (3, 9)],
    "black": [(6, 0), (6, 9), (9, 3), (9, 6)],
}

class AmazonasGame:
    def __init__(self):
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white"  # primer turno
        self.selected = None  # amazona seleccionada
        self.awaiting_arrow = False
        self.last_move = None  # ultima casilla movida
        self.finished = False  # si el juego ha terminado
        self.place_initial_pieces()  # coloca amazonas

    # coloca las amazonas en las posiciones iniciales
    def place_initial_pieces(self):
        for color, positions in START_POSITIONS.items():
            for row, col in positions:
                self.board[row][col] = color

    # verifica si una ruta entre dos casillas es valida
    def is_valid_path(self, r1, c1, r2, c2):
        if not (0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE):
            return False
        if self.board[r2][c2] != "":
            return False
        if r1 == r2:
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if self.board[r1][c] != "":
                    return False
        elif c1 == c2:
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if self.board[r][c1] != "":
                    return False
        elif abs(r2 - r1) == abs(c2 - c1):
            step_r = 1 if r2 > r1 else -1
            step_c = 1 if c2 > c1 else -1
            for i in range(1, abs(r2 - r1)):
                if self.board[r1 + i * step_r][c1 + i * step_c] != "":
                    return False
        else:
            return False
        return True

    # mueve la amazona si la ruta es valida
    def move_amazon(self, r1, c1, r2, c2):
        if not self.is_valid_path(r1, c1, r2, c2):
            return False
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = ""
        self.awaiting_arrow = True
        self.last_move = (r2, c2)
        return True

    # dispara una flecha desde la ultima posicion de la amazona movida
    def shoot_arrow(self, r_arrow, c_arrow):
        r, c = self.last_move
        if not self.is_valid_path(r, c, r_arrow, c_arrow):
            return False, None
        self.board[r_arrow][c_arrow] = "X"
        self.awaiting_arrow = False
        self.last_move = None
        self.selected = None
        self.turn = "black" if self.turn == "white" else "white"

        if not self.has_valid_moves(self.turn):
            winner = "Blanco" if self.turn == "black" else "Negro"
            self.finished = True
            return True, winner
        return True, None

    def has_valid_moves(self, player):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                            if self.board[nr][nc] == "" and self.is_valid_path(r, c, nr, nc):
                                if self.has_arrow_moves(nr, nc):
                                    return True
                            nr += dr
                            nc += dc
        return False

    def has_arrow_moves(self, r, c):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if self.board[nr][nc] == "" and self.is_valid_path(r, c, nr, nc):
                    return True
                nr += dr
                nc += dc
        return False

    # NUEVAS FUNCIONES PARA LA IA
    def get_all_valid_moves(self, player):
        """
        Retorna lista de todos los movimientos posibles para player:
        Cada movimiento es (r1, c1, r2, c2, r_arrow, c_arrow)
        """
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                            if self.board[nr][nc] == "" and self.is_valid_path(r, c, nr, nc):
                                for dr_a, dc_a in directions:
                                    ar, ac = nr + dr_a, nc + dc_a
                                    while 0 <= ar < BOARD_SIZE and 0 <= ac < BOARD_SIZE:
                                        if self.board[ar][ac] == "" and self.is_valid_path(nr, nc, ar, ac):
                                            moves.append((r, c, nr, nc, ar, ac))
                                        ar += dr_a
                                        ac += dc_a
                            nr += dr
                            nc += dc
        return moves

    def make_move(self, r1, c1, r2, c2, r_arrow, c_arrow):
        """
        Ejecuta movimiento completo: mover amazona + disparar flecha
        Retorna (terminado, ganador) o (False, None)
        """
        if not self.move_amazon(r1, c1, r2, c2):
            return False, None
        valid, winner = self.shoot_arrow(r_arrow, c_arrow)
        return valid and self.finished, winner


class AmazonasGUI:
    def __init__(self, root):
        self.root = root
        self.game = AmazonasGame()

        self.human_player = "white"
        self.ai_player = "black"

        # Fondo y fuente mejorados
        self.root.configure(bg="#f0f4f8")
        self.turn_label = tk.Label(root, text="Turno actual: Blanco", font=("Segoe UI", 16, "bold"), bg="#f0f4f8", fg="#333")
        self.turn_label.pack(pady=8)

        # Canvas con marco redondeado simulado
        self.canvas = tk.Canvas(root, width=TILE_SIZE * BOARD_SIZE, height=TILE_SIZE * BOARD_SIZE, bg="#dde6f0", highlightthickness=4, highlightbackground="#4863a0")
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        self.reset_button = tk.Button(root, text="Reiniciar juego", command=self.reset_game, font=("Segoe UI", 12, "bold"), bg="#4863a0", fg="white", activebackground="#375080", activeforeground="white")
        self.reset_button.pack(pady=10)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        light_color = "#eaecef"
        dark_color = "#8a9ecb"

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                fill = light_color if (row + col) % 2 == 0 else dark_color
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#627aac")

                piece = self.game.board[row][col]
                if piece == "white" or piece == "black":
                    # Crear un efecto de sombra para las piezas
                    shadow_offset = 3
                    base_color = "#f9f9f9" if piece == "white" else "#202020"
                    shadow_color = "#b0b0b0" if piece == "white" else "#000000"

                    # sombra
                    self.canvas.create_oval(
                        x1 + 10 + shadow_offset, y1 + 10 + shadow_offset, x2 - 10 + shadow_offset, y2 - 10 + shadow_offset,
                        fill=shadow_color, outline=""
                    )
                    # pieza principal
                    self.canvas.create_oval(
                        x1 + 10, y1 + 10, x2 - 10, y2 - 10,
                        fill=base_color, outline="#385170", width=3
                    )
                elif piece == "X":
                    self.canvas.create_rectangle(
                        x1 + 18, y1 + 18, x2 - 18, y2 - 18,
                        fill="#5a5a5a"
                    )

        # Resaltar pieza seleccionada
        if self.game.selected:
            r, c = self.game.selected
            x1 = c * TILE_SIZE
            y1 = r * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="#f9a825", width=4)

        # Mostrar visualmente las casillas válidas para mover o disparar flecha
        if self.game.selected and not self.game.awaiting_arrow:
            r, c = self.game.selected
            valid_moves = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if self.game.board[nr][nc] == "" and self.game.is_valid_path(r, c, nr, nc):
                        valid_moves.append((nr, nc))
                    else:
                        break
                    nr += dr
                    nc += dc
            for (vr, vc) in valid_moves:
                x1 = vc * TILE_SIZE + TILE_SIZE//3
                y1 = vr * TILE_SIZE + TILE_SIZE//3
                x2 = x1 + TILE_SIZE//3
                y2 = y1 + TILE_SIZE//3
                self.canvas.create_oval(x1, y1, x2, y2, fill="#f9a825", outline="")

        if self.game.awaiting_arrow and self.game.last_move:
            r, c = self.game.last_move
            # Resaltar casilla de amazona movida
            x1 = c * TILE_SIZE
            y1 = r * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            self.canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="#d32f2f", width=4)

            # Mostrar casillas válidas para disparar flecha
            valid_arrows = []
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                          (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if self.game.board[nr][nc] == "" and self.game.is_valid_path(r, c, nr, nc):
                        valid_arrows.append((nr, nc))
                    else:
                        break
                    nr += dr
                    nc += dc
            for (ar, ac) in valid_arrows:
                x1 = ac * TILE_SIZE + TILE_SIZE//3
                y1 = ar * TILE_SIZE + TILE_SIZE//3
                x2 = x1 + TILE_SIZE//3
                y2 = y1 + TILE_SIZE//3
                self.canvas.create_oval(x1, y1, x2, y2, fill="#d32f2f", outline="")

        self.update_turn_label()

    def update_turn_label(self):
        if self.game.finished:
            self.turn_label.config(text="Juego terminado")
        else:
            jugador = "Blanco" if self.game.turn == "white" else "Negro"
            self.turn_label.config(text=f"Turno actual: {jugador}")
    def on_click(self, event):
        if self.game.finished:
            return

        # Solo turno humano puede jugar
        if self.game.turn != self.human_player:
            return

        col = event.x // TILE_SIZE
        row = event.y // TILE_SIZE
        current = self.game.board[row][col]

        if self.game.awaiting_arrow:
            valid, winner = self.game.shoot_arrow(row, col)
            if valid:
                self.draw_board()
                if winner:
                    messagebox.showinfo("Juego terminado", f"¡{winner} gana!")
                else:
                    # Turno IA tras medio segundo
                    self.root.after(500, self.ai_move)
        elif self.game.selected:
            r1, c1 = self.game.selected
            if self.game.move_amazon(r1, c1, row, col):
                self.draw_board()
                # Esperando disparo flecha humano
            else:
                print("Movimiento inválido.")
        elif current == self.game.turn:
            self.game.selected = (row, col)

    def ai_move(self):
        if self.game.finished:
            return

        moves = self.game.get_all_valid_moves(self.ai_player)
        if not moves:
            messagebox.showinfo("Juego terminado", "¡Blanco gana!")
            self.game.finished = True
            self.update_turn_label()
            return

        move = random.choice(moves)
        r1, c1, r2, c2, r_arrow, c_arrow = move
        finished, winner = self.game.make_move(r1, c1, r2, c2, r_arrow, c_arrow)
        self.draw_board()
        if finished and winner:
            messagebox.showinfo("Juego terminado", f"¡{winner} gana!")
        else:
            self.update_turn_label()

    def reset_game(self):
        self.game = AmazonasGame()
        self.draw_board()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Juego de las Amazonas")
    app = AmazonasGUI(root)
    root.mainloop()
