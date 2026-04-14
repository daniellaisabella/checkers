RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
BLUE = (0, 0, 255)

class Piece:
    def __init__(self, row: int, col: int, color: tuple):
        self.row = row
        self.col = col
        self.color = color
        self.king = False

    def move(self, row: int, col: int):
        self.row = row
        self.col = col

    def make_king(self):
        self.king = True

    def __repr__(self):
        return f"<Piece {self.color} row={self.row} col={self.col} king={self.king}>"
