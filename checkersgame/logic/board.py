import pygame

from pieces import Piece, RED, WHITE, BLACK, GREY, BLUE

ROWS = COLS = 8
SQUARE_SIZE = 80

LIGHT_SQUARE = (235, 235, 208)
DARK_SQUARE = (119, 148, 85)

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def draw_squares(self, win):
        win.fill(LIGHT_SQUARE)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2):
                pygame.draw.rect(
                    win,
                    DARK_SQUARE,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw(self, win):
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece is not None:
                    self.draw_piece(win, piece)

    def draw_piece(self, win, piece):
        radius = SQUARE_SIZE // 2 - 10
        x = piece.col * SQUARE_SIZE + SQUARE_SIZE // 2
        y = piece.row * SQUARE_SIZE + SQUARE_SIZE // 2
        pygame.draw.circle(win, BLACK, (x, y), radius + 2)
        pygame.draw.circle(win, piece.color, (x, y), radius)
        if piece.king:
            pygame.draw.circle(win, BLUE, (x, y), radius // 3)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = None, piece
        piece.move(row, col)
        if row == 0 and piece.color == WHITE:
            piece.make_king()
            self.white_kings += 1
        elif row == ROWS - 1 and piece.color == RED:
            piece.make_king()
            self.red_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece is not None:
                if piece.color == RED:
                    self.red_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.red_left <= 0:
            return "WHITE"
        elif self.white_left <= 0:
            return "RED"
        return None

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=None):
        if skipped is None:
            skipped = []

        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    next_row = r + step
                    moves.update(self._traverse_left(next_row, stop, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(next_row, stop, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=None):
        if skipped is None:
            skipped = []

        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current is None:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    next_row = r + step
                    moves.update(self._traverse_left(next_row, stop, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(next_row, stop, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves
