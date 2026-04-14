import pygame

from board import Board, SQUARE_SIZE, ROWS, COLS
from pieces import RED, WHITE

HIGHLIGHT_COLOR = (0, 255, 0)

class Game:
    def __init__(self):
        self._init()

    def _init(self):
        self.selected = None
        self.board = Board()
        self.turn = RED
        self.valid_moves = {}

    def update(self, win):
        self.board.draw(win)
        self.draw_valid_moves(win)
        pygame.display.update()

    def reset(self):
        self._init()

    def select(self, row, col):
        if self.selected:
            moved = self._move(row, col)
            if not moved:
                self.selected = None
                self.select(row, col)

        piece = self.board.get_piece(row, col)
        if piece is not None and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True

        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
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
        self.valid_moves = {}
        self.turn = WHITE if self.turn == RED else RED
