import pygame

from .board import Board, SQUARE_SIZE
from .pieces import PieceColor

HIGHLIGHT_COLOR = (0, 255, 0)

class Game:
    def __init__(self):
        self._init()

    def _init(self):
        self.selected = None
        self.forced_piece = None
        self.board = Board()
        self.turn = PieceColor.BLACK
        self.valid_moves = {}
        self.player_color = PieceColor.BLACK
        self.search_mode = "depth"
        self.search_depth = 4
        self.search_time_seconds = 1.0

    def update(self, win):
        self.board.draw(win)
        self.draw_valid_moves(win)

    def set_ai_preferences(self, player_color, search_mode, depth, time_seconds):
        self.player_color = player_color
        self.search_mode = search_mode
        self.search_depth = depth
        self.search_time_seconds = time_seconds

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            moved = self._move(row, col)
            if moved:
                return True
            if self.forced_piece is not None:
                return False
            if self.selected and (row, col) not in self.valid_moves:
                self.selected = None
                self.valid_moves = {}

        piece = self.board.get_piece(row, col)
        if piece is None or piece.color != self.turn:
            return False

        if self.forced_piece is not None and piece != self.forced_piece:
            return False

        moves = self.board.get_valid_moves(piece)
        if self._player_has_capture(self.turn):
            moves = self._capture_only(moves)
            if not moves:
                return False

        self.selected = piece
        self.valid_moves = moves
        return True

    def _capture_only(self, moves):
        return {move: skipped for move, skipped in moves.items() if skipped}

    def _player_has_capture(self, color):
        for piece in self.board.get_all_pieces(color):
            moves = self.board.get_valid_moves(piece)
            if any(skipped for skipped in moves.values()):
                return True
        return False

    def _move(self, row, col):
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
                next_moves = self._capture_only(self.board.get_valid_moves(self.selected))
                if next_moves:
                    self.forced_piece = self.selected
                    self.valid_moves = next_moves
                    return True

            self.change_turn()
            return True
        return False

    def draw_valid_moves(self, win):
        for move in self.valid_moves:
            row, col = move
            pygame.draw.circle(
                win,
                HIGHLIGHT_COLOR,
                (
                    col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    row * SQUARE_SIZE + SQUARE_SIZE // 2,
                ),
                10,
            )

    def change_turn(self):
        self.selected = None
        self.forced_piece = None
        self.valid_moves = {}
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK
