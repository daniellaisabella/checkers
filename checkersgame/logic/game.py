import pygame
from ..ai.minmax import minmax
from ..ai.minmax import evaluate
from .board import Board, SQUARE_SIZE
from .pieces import PieceColor

HIGHLIGHT_COLOR = (0, 255, 0) # farven for at fremhæve gyldige træk på brættet, i dette tilfælde grøn.

# Dette modul indeholder Game-klassen, 
# som håndterer den overordnede spillogik, 
# spillerens tur, 
# valg af brikker og gyldige træk. 
# Den bruger Board-klassen til at interagere med brættet og brikkerne, 
# og den håndterer også tegningen af gyldige træk på skærmen. 

class Game:
    def __init__(self):
        self._init()

    def _init(self):
        self.selected = None
        self.forced_piece = None
        self.board = Board()
        self.board_flipped = False
        self.has_started = False
        self.turn = PieceColor.BLACK
        self.valid_moves = {}
        self.player_color = PieceColor.BLACK
        self.search_mode = "both"
        self.search_depth = 4
        self.search_time_seconds = 1.0
        self.force_capture = True

    def update(self, win):
        self.board.draw(win, flipped=self.board_flipped)
        self.draw_valid_moves(win, flipped=self.board_flipped)

    def set_board_flipped(self, board_flipped):
        self.board_flipped = board_flipped

    def set_ai_preferences(self, player_color, search_mode, depth, time_seconds, forced_jump=True):
        color_changed = player_color != self.player_color
        self.player_color = player_color
        self.search_mode = search_mode
        self.search_depth = depth
        self.search_time_seconds = time_seconds
        self.force_capture = forced_jump

        # Når spilleren skifter farve i menuen, skifter vi også aktiv tur,
        # så man med det samme kan lave træk med den valgte farve.
        if color_changed:
            self.turn = self.player_color
            self.selected = None
            self.forced_piece = None
            self.valid_moves = {}

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
        if self.force_capture and self._player_has_capture(self.turn):
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
            self.has_started = True
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
                # tjek om brikken kan hoppe igen:
                next_moves = self._capture_only(self.board.get_valid_moves(self.selected))
                if next_moves:
                    self.forced_piece = self.selected 
                    self.valid_moves = next_moves
                    return True

            self.change_turn()
        
            return True
        return False
    

    def ai_move(self):
        maximizing_player = self.turn == PieceColor.WHITE
        _, best_board_state = minmax(
            self.board,
            self.search_depth,
            maximizing_player,
            float('-inf'),
            float('inf'),
            self.force_capture,
        )

        if best_board_state is None:
            return False

        self.board = best_board_state
        self.has_started = True
        self.change_turn()
        return True
        

# tegne
    def draw_valid_moves(self, win, flipped=False):
        for move in self.valid_moves: # self.valid.moves kommer fra Board-klassen
            row, col = move
            draw_col = 7 - col if flipped else col
            draw_row = 7 - row if flipped else row
            pygame.draw.circle(
                win,
                HIGHLIGHT_COLOR,
                (
                    draw_col * SQUARE_SIZE + SQUARE_SIZE // 2,
                    draw_row * SQUARE_SIZE + SQUARE_SIZE // 2,
                ),
                10,
            )

    def change_turn(self):
        if self.board.winner() is not None:
            print(self.board.winner())
            return 
        
        self.selected = None
        self.forced_piece = None
        self.valid_moves = {} # denne linje rydder gyldige træk, når turen skifter
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK

        print(evaluate(self.board))

        if self.turn != self.player_color and self.board.winner() is None:
            self.ai_move()
