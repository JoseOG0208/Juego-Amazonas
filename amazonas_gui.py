import tkinter as tk
from tkinter import messagebox

TILE_SIZE = 60
BOARD_SIZE = 10

START_POSITIONS = {
    "white": [(0, 3), (0, 6), (3, 0), (3, 9)],
    "black": [(6, 0), (6, 9), (9, 3), (9, 6)],
}

class AmazonasGame:
    def __init__(self):
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white"
        self.selected = None
        self.awaiting_arrow = False
        self.last_move = None
        self.place_initial_pieces()

    def place_initial_pieces(self):
        for color, positions in START_POSITIONS.items():
            for row, col in positions:
                self.board[row][col] = color

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

    def move_amazon(self, r1, c1, r2, c2):
        if not self.is_valid_path(r1, c1, r2, c2):
            return False
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = ""
        self.awaiting_arrow = True
        self.last_move = (r2, c2)
        return True

    def shoot_arrow(self, r_arrow, c_arrow):
        r, c = self.last_move
        if not self.is_valid_path(r, c, r_arrow, c_arrow):
            return False
        self.board[r_arrow][c_arrow] = "X"
        self.awaiting_arrow = False
        self.last_move = None
        self.selected = None
        self.turn = "black" if self.turn == "white" else "white"

        # Verificar si el siguiente jugador puede moverse
        if not self.has_valid_moves(self.turn):
            winner = "Blanco" if self.turn == "black" else "Negro"
            messagebox.showinfo("Juego terminado", f"¡{winner} gana!")
        return True

    def has_valid_moves(self, player):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] == player:
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == "":
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
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.board[nr][nc] == "":
                return True
        return False

class AmazonasGUI:
    def __init__(self, root):
        self.game = AmazonasGame()
        self.root = root
        self.canvas = tk.Canvas(root, width=TILE_SIZE*BOARD_SIZE, height=TILE_SIZE*BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.reset_button = tk.Button(root, text="Reiniciar juego", command=self.reset_game)
        self.reset_button.pack(pady=10)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = col * TILE_SIZE
                y1 = row * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                fill = "#EEE" if (row + col) % 2 == 0 else "#AAA"
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

    def on_click(self, event):
        col = event.x // TILE_SIZE
        row = event.y // TILE_SIZE
        current = self.game.board[row][col]

        if self.game.awaiting_arrow:
            if self.game.shoot_arrow(row, col):
                self.draw_board()
            else:
                print("Flecha inválida.")
        elif self.game.selected:
            r1, c1 = self.game.selected
            if self.game.move_amazon(r1, c1, row, col):
                self.draw_board()
            else:
                print("Movimiento inválido.")
        elif current == self.game.turn:
            self.game.selected = (row, col)

    def reset_game(self):
        self.game = AmazonasGame()
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Juego de las Amazonas - Local VS")
    app = AmazonasGUI(root)
    root.mainloop()
