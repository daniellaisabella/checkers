from ..logic.pieces import PieceColor
from ..logic.pieces import Piece
from ..logic.board import Board

# Array of weights for white for static evalution function
WHITE_WEIGHTS = [
    [0, 4, 0, 4, 0, 4, 0, 4],
    [2, 0, 3, 0, 3, 0, 2, 0],
    [0, 2, 0, 2, 0, 2, 0, 2],
    [2, 0, 2, 0, 2, 0, 2, 0],
    [0, 1, 0, 2, 0, 2, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0]
]


# Array of weights for black for static evalution function
BLACK_WEIGHTS = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [-1, 0, -2, 0, -2, 0, -1, 0],
    [0, -2, 0, -2, 0, -2, 0, -2],
    [-2, 0, -2, 0, -2, 0, -2, 0],
    [0, -2, 0, -3, 0, -3, 0, -2],
    [-4, 0, -4, 0, -4, 0, -4, 0]
]


# evaluate the board state and return a score
def evaluate(board_state):
    # simple static evaluation function: count the pieces
    score = 0
    for row in board_state.board:
        for piece in row:
            if piece is not None:
                if piece.color == PieceColor.WHITE:
                    if piece.king: 
                        score += 2
                    score += 1
                    piece_score = WHITE_WEIGHTS[piece.row][piece.col]
                    score += piece_score
                else:
                    if piece.color == PieceColor.BLACK:
                        if piece.king:
                            score -= 2
                        score -= 1
                    piece_score = BLACK_WEIGHTS[piece.row][piece.col]
                    score += piece_score
    return score


def minmax(position, depth, maximizing_player):
    if depth == 0:
        return evaluate(position), position

    if maximizing_player:
        max_eval = -10000
        best_board_state = None
        for next_board_state in get_valid_moves(position, PieceColor.WHITE):
            evaluation = minmax(next_board_state, depth - 1, False)[0]
            max_eval = max(max_eval, evaluation)
            if max_eval == evaluation:
                best_board_state = next_board_state
        return max_eval, best_board_state
    else:
        min_eval = 10000
        best_board_state = None
        for next_board_state in get_valid_moves(position, PieceColor.BLACK):
            evaluation = minmax(next_board_state, depth - 1, True)[0]
            min_eval = min(min_eval, evaluation)
            if min_eval == evaluation:
                best_board_state = next_board_state
        return min_eval, best_board_state


def clone_board_state(source_board):
    cloned_board = Board.__new__(Board)

    # Copy logical counters used by evaluation/winner logic.
    cloned_board.black_left = source_board.black_left
    cloned_board.white_left = source_board.white_left
    cloned_board.black_kings = source_board.black_kings
    cloned_board.white_kings = source_board.white_kings

    # Reuse loaded images to avoid reloading assets during search.
    cloned_board.board_image = source_board.board_image
    cloned_board.flipped_board_image = source_board.flipped_board_image
    cloned_board.black_piece_image = source_board.black_piece_image
    cloned_board.white_piece_image = source_board.white_piece_image
    cloned_board.black_king_image = source_board.black_king_image
    cloned_board.white_king_image = source_board.white_king_image

    cloned_board.board = []
    for row in source_board.board:
        cloned_row = []
        for piece in row:
            if piece is None:
                cloned_row.append(None)
            else:
                copied_piece = Piece(piece.row, piece.col, piece.color)
                copied_piece.king = piece.king
                cloned_row.append(copied_piece)
        cloned_board.board.append(cloned_row)

    return cloned_board
    
def get_valid_moves(current_board_state, color):
    next_board_states = []
    for row in current_board_state.board:
        for piece in row:
            if piece is not None and piece.color == color:
                piece_valid_moves = current_board_state.get_valid_moves(piece)
                for (move_row, move_col), skipped in piece_valid_moves.items():
                    next_board_state = clone_board_state(current_board_state)
                    piece_copy = next_board_state.get_piece(piece.row, piece.col)
                    next_board_state.move(piece_copy, move_row, move_col)

                    if skipped:
                        skipped_pieces_on_copy = []
                        for skipped_piece in skipped:
                            copied_skipped_piece = next_board_state.get_piece(skipped_piece.row, skipped_piece.col)
                            if copied_skipped_piece is not None:
                                skipped_pieces_on_copy.append(copied_skipped_piece)
                        next_board_state.remove(skipped_pieces_on_copy)

                    next_board_states.append(next_board_state)
    return next_board_states

