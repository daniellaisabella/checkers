import pygame
import sys

from checkersgame.logic.board import ROWS, COLS, SQUARE_SIZE
from checkersgame.logic.game import Game
from checkersgame.ui.side_panel import PANEL_WIDTH, SidePanel

BOARD_WIDTH = COLS * SQUARE_SIZE
WIDTH = BOARD_WIDTH + PANEL_WIDTH
HEIGHT = ROWS * SQUARE_SIZE
FPS = 60


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if side_panel.handle_click(pos):
                    game.set_ai_preferences(
                        player_color=side_panel.settings.player_color,
                        search_mode=side_panel.settings.search_mode,
                        depth=side_panel.settings.depth,
                        time_seconds=side_panel.settings.time_seconds,
                    )
                    continue

                row, col = get_row_col_from_mouse(pos)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    game.select(row, col)

        game.update(win)
        side_panel.draw(win)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
