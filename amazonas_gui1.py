import tkinter as tk

TILE_SIZE = 60
BOARD_SIZE = 10

#posiciones iniciales de las amazonas
START_POSITIONS = {
    "white": [(0, 3), (0, 6), (3, 0), (3, 9)],
    "black": [(6, 0), (6, 9), (9, 3), (9, 6)],
}

class AmazonasGame:
    def __init__(self):
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = "white"
        self.finished = False
        self.place_initial_pieces()

    #coloca las piezas de cada jugador en sus posiciones iniciales
    def place_initial_pieces(self):
        for color, positions in START_POSITIONS.items():
            for row, col in positions:
                self.board[row][col] = color

#interfaz gráfica
class AmazonasGUI:
    def __init__(self, root):
        self.root = root
        self.game = AmazonasGame()

        #muestra el turno actual
        self.turn_label = tk.Label(root, text="Turno actual: Blanco", font=("Helvetica", 14, "bold"))
        self.turn_label.pack(pady=5)

        self.canvas = tk.Canvas(root, width=TILE_SIZE * BOARD_SIZE, height=TILE_SIZE * BOARD_SIZE)
        self.canvas.pack()

        #botón de reinicio
        self.reset_button = tk.Button(root, text="Reiniciar juego", state="disabled")
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
                fill = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

                piece = self.game.board[row][col] #verifica si hay pieza en esa casilla
                if piece == "white" or piece == "black":
                    self.canvas.create_oval(
                        x1 + 10, y1 + 10, x2 - 10, y2 - 10,
                        fill=piece, outline="blue", width=2
                    )

        self.update_turn_label() #actualiza el texto del turno actual

    # actualiza la etiqueta con el nombre del jugador que tiene el turno
    def update_turn_label(self):
        jugador = "Blanco" if self.game.turn == "white" else "Negro"
        self.turn_label.config(text=f"Turno actual: {jugador}")

#ejecutar la pantalla visual
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Juego de las Amazonas (Solo visual)")
    app = AmazonasGUI(root)
    root.mainloop()
