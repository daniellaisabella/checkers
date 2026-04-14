import pygame
import sys

from board import ROWS, COLS, SQUARE_SIZE
from game import Game

WIDTH = COLS * SQUARE_SIZE
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

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_row_col_from_mouse(pos)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    game.select(row, col)

        game.update(win)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
