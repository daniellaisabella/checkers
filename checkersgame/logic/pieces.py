from enum import Enum


class PieceColor(Enum):
    # Farven beskriver hvilken side en brik tilhører.
    BLACK = "black"
    WHITE = "white"


# En Piece repræsenterer én brik på brættet med position, side og king-status.
class Piece:
    def __init__(self, row: int, col: int, color: PieceColor):
        self.row = row
        self.col = col
        self.color = color
        self.king = False

    # Opdater brikkens position, når den flyttes.
    def move(self, row: int, col: int):
        self.row = row
        self.col = col

    # Markér brikken som en king, så den kan bevæge sig baglæns.
    def make_king(self):
        self.king = True

    # Hjælper ved debugging, så en brik kan udskrives læsbart.
    def __repr__(self):
        return f"<Piece {self.color.value} row={self.row} col={self.col} king={self.king}>"
