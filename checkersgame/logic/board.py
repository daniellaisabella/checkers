from pathlib import Path

import pygame

from .pieces import Piece, PieceColor

ROWS = COLS = 8
SQUARE_SIZE = 80

# Mappen med sprites til bræt og brikker.
ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"

LIGHT_SQUARE = (235, 235, 208)
DARK_SQUARE = (119, 148, 85)

class Board:
    def __init__(self):
        # Board holder den logiske tilstand og de billeder, som bruges til rendering.
        self.board = []
        self.black_left = self.white_left = 12
        self.black_kings = self.white_kings = 0
        # Brættet og brikkerne læses fra assets og skaleres til den faste størrelse.
        self.board_image = self._load_image("Board_Checkers_x2.png", (COLS * SQUARE_SIZE, ROWS * SQUARE_SIZE))
        self.black_piece_image = self._load_image("Stone_Black_x2.png", (SQUARE_SIZE, SQUARE_SIZE))
        self.white_piece_image = self._load_image("Stone_White_x2.png", (SQUARE_SIZE, SQUARE_SIZE))
        self.black_king_image = self._load_image("Stone_Black_2_x2.png", (SQUARE_SIZE, SQUARE_SIZE))
        self.white_king_image = self._load_image("Stone_White_2_x2.png", (SQUARE_SIZE, SQUARE_SIZE))
        self.create_board()

    def _load_image(self, name, size):
        # Hjælperfunktion så alle sprites bliver loadet og skaleret på samme måde.
        image = pygame.image.load(str(ASSETS_DIR / name)).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    def draw_squares(self, win):
        # Baggrunden er et færdigtegnet bræt, så vi blitter det direkte.
        win.blit(self.board_image, (0, 0))

    def create_board(self):
        # Opret den standardiserede startopstilling: sorte øverst, hvide nederst.
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row].append(Piece(row, col, PieceColor.BLACK))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, PieceColor.WHITE))
                    else:
                        self.board[row].append(None)
                else:
                    self.board[row].append(None)

    def draw(self, win):
        # Tegn først brættet og derefter alle aktive brikker ovenpå.
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece is not None:
                    self.draw_piece(win, piece)

    def draw_piece(self, win, piece):
        # Vælg den korrekte sprite ud fra side og om brikken er en king.
        x = piece.col * SQUARE_SIZE
        y = piece.row * SQUARE_SIZE
        if piece.color == PieceColor.BLACK:
            image = self.black_king_image if piece.king else self.black_piece_image
        else:
            image = self.white_king_image if piece.king else self.white_piece_image
        win.blit(image, (x, y))

    def move(self, piece, row, col):
        # Flyt brikken i den logiske board-matrix og opdater dens position.
        self.board[piece.row][piece.col], self.board[row][col] = None, piece
        piece.move(row, col)
        # Promote til king, når en brik når den modsatte ende af brættet.
        if row == ROWS - 1 and piece.color == PieceColor.BLACK:
            piece.make_king()
            self.black_kings += 1
        elif row == 0 and piece.color == PieceColor.WHITE:
            piece.make_king()
            self.white_kings += 1

    def get_piece(self, row, col):
        return self.board[row][col]

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece is not None and piece.color == color:
                    pieces.append(piece)
        return pieces

    def remove(self, pieces):
        # Fjern fangede brikker fra board og reducer antallet af brikker på den side.
        for piece in pieces:
            self.board[piece.row][piece.col] = None
            if piece is not None:
                if piece.color == PieceColor.BLACK:
                    self.black_left -= 1
                else:
                    self.white_left -= 1

    def winner(self):
        if self.black_left <= 0:
            return "WHITE"
        elif self.white_left <= 0:
            return "BLACK"
        return None

    def get_valid_moves(self, piece):
        # Byg en map over gyldige træk, inklusive hop over modstandere.
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == PieceColor.WHITE or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == PieceColor.BLACK or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=None):
        # Rekursiv søgning mod venstre, som også understøtter kædespring.
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
        # Samme logik som _traverse_left, men spejlet mod højre.
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
