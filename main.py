import pygame
import sys

from checkersgame.logic.board import ROWS, COLS, SQUARE_SIZE
from checkersgame.logic.game import Game
from checkersgame.logic.pieces import PieceColor
from checkersgame.ui.side_panel import PANEL_WIDTH, SidePanel

BOARD_WIDTH = COLS * SQUARE_SIZE
WIDTH = BOARD_WIDTH + PANEL_WIDTH
HEIGHT = ROWS * SQUARE_SIZE
FPS = 60


def get_row_col_from_mouse(pos, flipped=False):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    if flipped:
        row = ROWS - 1 - row
        col = COLS - 1 - col
    return row, col


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers")
    clock = pygame.time.Clock()
    game = Game()
    side_panel = SidePanel(BOARD_WIDTH, HEIGHT)

    running = True
    while running:
        clock.tick(FPS)
        side_panel.set_settings_locked(game.has_started)
        side_panel.set_start_button_visible(
            not game.has_started and side_panel.settings.player_color == PieceColor.WHITE
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                panel_action = side_panel.handle_click(pos)
                if panel_action == "start":
                    game.start_game()
                    continue
                if panel_action == "restart":
                    game.reset()
                    game.set_ai_preferences(
                        player_color=side_panel.settings.player_color,
                        search_mode="both",
                        depth=side_panel.settings.depth,
                        time_seconds=side_panel.settings.time_seconds,
                        forced_jump=side_panel.settings.forced_jump,
                    )
                    game.set_board_flipped(side_panel.settings.board_flipped)
                    continue

                if panel_action == "settings":
                    game.set_ai_preferences(
                        player_color=side_panel.settings.player_color,
                        search_mode="both",
                        depth=side_panel.settings.depth,
                        time_seconds=side_panel.settings.time_seconds,
                        forced_jump=side_panel.settings.forced_jump,
                    )
                    game.set_board_flipped(side_panel.settings.board_flipped)
                    continue

                if panel_action == "panel":
                    continue

                row, col = get_row_col_from_mouse(pos, flipped=side_panel.settings.board_flipped)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    game.select(row, col)

            elif event.type == pygame.KEYDOWN:
                if side_panel.handle_keydown(event):
                    game.set_ai_preferences(
                        player_color=side_panel.settings.player_color,
                        search_mode="both",
                        depth=side_panel.settings.depth,
                        time_seconds=side_panel.settings.time_seconds,
                        forced_jump=side_panel.settings.forced_jump,
                    )
                    game.set_board_flipped(side_panel.settings.board_flipped)
                    continue

        side_panel.set_settings_locked(game.has_started)
        side_panel.set_start_button_visible(
            not game.has_started and side_panel.settings.player_color == PieceColor.WHITE
        )
        game.update(win)
        side_panel.draw(win)

        # Display game status (winner or stalemate)
        if game.game_status is not None:
            font = pygame.font.SysFont('arial', 48, bold=True)
            if game.game_status == "STALEMATE":
                status_message = "STALEMATE"
                color = (100, 149, 237)  # blue
            else:
                status_message = game.game_status
                color = (255, 215, 0)  # Gold
            
            text_surface = font.render(status_message, True, color)
            text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            win.blit(text_surface, text_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
