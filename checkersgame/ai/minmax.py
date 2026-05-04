from ..logic.board import Board
from ..logic.pieces import PieceColor
# Array of weights for white for static evalution function
WHITE_WEIGHTS = [
    [4, 0, 4, 0, 4, 0, 4, 0],
    [0, 2, 0, 3, 0, 3, 0, 2],
    [2, 0, 2, 0, 2, 0, 2, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [1, 0, 2, 0, 2, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]


# Array of weights for black for static evalution function
BLACK_WEIGHTS = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 2, 0, 2, 0, 1, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [2, 0, 2, 0, 2, 0, 2, 0],
    [0, 2, 0, 3, 0, 3, 0, 2],
    [4, 0, 4, 0, 4, 0, 4, 0]
]


# evaluate the board state and return a score
def evaluate(board):
    # simple static evaluation function: count the pieces
    score = 0
    for row in board.board:
        for piece in row:
            if piece is not None:
                if piece.color == PieceColor.WHITE:
                    if piece.king:
                        score += 2
                    score += 1
                else:
                    if piece.color == PieceColor.BLACK:
                        if piece.king:
                            score -= 2
                        score -= 1
    return score