import tkinter as tk
from tkinter import messagebox

#tamaño del tablero y casillas
TILE_SIZE = 60
BOARD_SIZE = 10

#posiciones de inicio para cada jugador
START_POSITIONS = {
    "white": [(0, 3), (0, 6), (3, 0), (3, 9)],
    "black": [(6, 0), (6, 9), (9, 3), (9, 6)],
}

class AmazonasGame:
    def __init__(self):
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white" #primer turno
        self.selected = None #amazona selecionada
        self.awaiting_arrow = False
        self.last_move = None #ultima casilla movida
        self.finished = False #si el juego ha termiando
        self.place_initial_pieces() #coloca amazonas

    #coloca las amazonas en las posiciones iniciales
    def place_initial_pieces(self):
        for color, positions in START_POSITIONS.items():
            for row, col in positions:
                self.board[row][col] = color

    #verifica  si una ruta entre dos casillas es valida
    def is_valid_path(self, r1, c1, r2, c2):
        if not (0 <= r2 < BOARD_SIZE and 0 <= c2 < BOARD_SIZE):
            return False
        #movimiento horicontal
        if self.board[r2][c2] != "":
            return False
        if r1 == r2:
            step = 1 if c2 > c1 else -1
            for c in range(c1 + step, c2, step):
                if self.board[r1][c] != "":
                    return False
        #movimiento vertical
        elif c1 == c2:
            step = 1 if r2 > r1 else -1
            for r in range(r1 + step, r2, step):
                if self.board[r][c1] != "":
                    return False
        #movimiento diagonal
        elif abs(r2 - r1) == abs(c2 - c1):
            step_r = 1 if r2 > r1 else -1
            step_c = 1 if c2 > c1 else -1
            for i in range(1, abs(r2 - r1)):
                if self.board[r1 + i * step_r][c1 + i * step_c] != "":
                    return False
        else:
            return False
        return True

    #mueve la aazona si la ruta es valida
    def move_amazon(self, r1, c1, r2, c2):
        if not self.is_valid_path(r1, c1, r2, c2):
            return False
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = ""
        self.awaiting_arrow = True
        self.last_move = (r2, c2)
        return True

    #dispara una flecha desde la ultima posicion de la amazonas movida
    def shoot_arrow(self, r_arrow, c_arrow):
        r, c = self.last_move
        if not self.is_valid_path(r, c, r_arrow, c_arrow):
            return False, None
        self.board[r_arrow][c_arrow] = "X"
        self.awaiting_arrow = False
        self.last_move = None
        self.selected = None
        self.turn = "black" if self.turn == "white" else "white"

        #verifica si el jugador puede hacer mas movimientos validos
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

    #verifica si desde una casilla se puede disparar una flecha
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

#interfaz grafica
class AmazonasGUI:
    def __init__(self, root):
        self.root = root
        self.game = AmazonasGame()

        #turno actual
        self.turn_label = tk.Label(root, text="Turno actual: Blanco", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(pady=5)

        #canvas para el tablero
        self.canvas = tk.Canvas(root, width=TILE_SIZE * BOARD_SIZE, height=TILE_SIZE * BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        #boton para reiniciar el juego
        self.reset_button = tk.Button(root, text="Reiniciar juego", command=self.reset_game)
        self.reset_button.pack(pady=10)

        self.draw_board()

    #dibuja el tablero y las piezas 
    def draw_board(self):
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                fill = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

                piece = self.game.board[row][col]
                if piece == "white" or piece == "black":
                    self.canvas.create_oval(
                        x1 + 10, y1 + 10, x2 - 10, y2 - 10,
                        fill=piece, outline="blue", width=2
                    )
                elif piece == "X":
                    self.canvas.create_rectangle(
                        x1 + 15, y1 + 15, x2 - 15, y2 - 15,
                        fill="gray20"
                    )

        self.update_turn_label()

    #actualiza el texto del turno actual
    def update_turn_label(self):
        if self.game.finished:
            self.turn_label.config(text="Juego terminado")
        else:
            jugador = "Blanco" if self.game.turn == "white" else "Negro"
            self.turn_label.config(text=f"Turno actual: {jugador}")

    #controla el click del mouse en el tablero
    def on_click(self, event):
        if self.game.finished:
            return

        col = event.x // TILE_SIZE
        row = event.y // TILE_SIZE
        current = self.game.board[row][col]

        #disparo de flecha
        if self.game.awaiting_arrow:
            valid, winner = self.game.shoot_arrow(row, col)
            if valid:
                self.draw_board()
                if winner:
                    messagebox.showinfo("Juego terminado", f"¡{winner} gana!")
        #movimiento de amazona
        elif self.game.selected:
            r1, c1 = self.game.selected
            if self.game.move_amazon(r1, c1, row, col):
                self.draw_board()
            else:
                print("Movimiento inválido.")
        #seleccion de amazona
        elif current == self.game.turn:
            self.game.selected = (row, col)

    #reinicia el juego
    def reset_game(self):
        self.game = AmazonasGame()
        self.draw_board()

#ejecuta la interfaz
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Juego de las Amazonas")
    app = AmazonasGUI(root)
    root.mainloop()
