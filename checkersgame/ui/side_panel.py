from dataclasses import dataclass
from pathlib import Path

import pygame

from checkersgame.logic.pieces import PieceColor

PANEL_WIDTH = 320

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"

TEXT_COLOR = (237, 236, 224)
MUTED_TEXT_COLOR = (193, 191, 175)
SELECTED_BORDER = (255, 222, 119)
BUTTON_BG = (58, 69, 56)
BUTTON_BG_ALT = (76, 88, 72)
BUTTON_BORDER = (26, 34, 24)


@dataclass
class PanelSettings:
    player_color: PieceColor = PieceColor.BLACK
    search_mode: str = "depth"
    depth: int = 4
    time_seconds: float = 1.0


class SpriteButton:
    def __init__(self, rect, label, value, icon=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.value = value
        self.icon = icon

    def draw(self, win, font, selected=False, alternate=False):
        bg = BUTTON_BG_ALT if alternate else BUTTON_BG
        pygame.draw.rect(win, bg, self.rect, border_radius=12)
        border_color = SELECTED_BORDER if selected else BUTTON_BORDER
        border_width = 4 if selected else 2
        pygame.draw.rect(win, border_color, self.rect, border_width, border_radius=12)

        text_x = self.rect.x + 14
        if self.icon is not None:
            icon_rect = self.icon.get_rect()
            icon_rect.centery = self.rect.centery
            icon_rect.left = self.rect.left + 10
            win.blit(self.icon, icon_rect)
            text_x = icon_rect.right + 8

        text_surface = font.render(self.label, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = text_x
        win.blit(text_surface, text_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class SidePanel:
    def __init__(self, board_width, height):
        self.board_width = board_width
        self.height = height
        self.rect = pygame.Rect(board_width, 0, PANEL_WIDTH, height)
        self.settings = PanelSettings()

        self.title_font = pygame.font.SysFont("georgia", 34, bold=True)
        self.header_font = pygame.font.SysFont("georgia", 24, bold=True)
        self.body_font = pygame.font.SysFont("georgia", 20)
        self.meta_font = pygame.font.SysFont("georgia", 17)

        self.background = self._load_image("Board_Checkers_x2.png", (PANEL_WIDTH, height))
        self.black_icon = self._load_image("Stone_Black_x2.png", (42, 42))
        self.white_icon = self._load_image("Stone_White_x2.png", (42, 42))
        self.depth_icon = self._load_image("Stone_Black_2_x2.png", (36, 36))
        self.time_icon = self._load_image("Stone_White_2_x2.png", (36, 36))

        self.color_buttons = self._build_color_buttons()
        self.mode_buttons = self._build_mode_buttons()
        self.depth_buttons = self._build_depth_buttons()
        self.time_buttons = self._build_time_buttons()

    def _load_image(self, name, size):
        image = pygame.image.load(str(ASSETS_DIR / name)).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    def _build_color_buttons(self):
        x = self.board_width + 20
        y = 126
        width = PANEL_WIDTH - 40
        height = 56
        return [
            SpriteButton((x, y, width, height), "Sort", PieceColor.BLACK, self.black_icon),
            SpriteButton((x, y + 68, width, height), "Hvid", PieceColor.WHITE, self.white_icon),
        ]

    def _build_mode_buttons(self):
        x = self.board_width + 20
        y = 298
        width = PANEL_WIDTH - 40
        height = 52
        return [
            SpriteButton((x, y, width, height), "Dybde", "depth", self.depth_icon),
            SpriteButton((x, y + 62, width, height), "Tid", "time", self.time_icon),
        ]

    def _build_depth_buttons(self):
        x = self.board_width + 20
        y = 450
        width = (PANEL_WIDTH - 52) // 2
        height = 48
        values = [2, 4, 6, 8]
        buttons = []
        for index, value in enumerate(values):
            row = index // 2
            col = index % 2
            bx = x + col * (width + 12)
            by = y + row * (height + 12)
            buttons.append(SpriteButton((bx, by, width, height), f"Dybde {value}", value))
        return buttons

    def _build_time_buttons(self):
        x = self.board_width + 20
        y = 450
        width = (PANEL_WIDTH - 52) // 2
        height = 48
        values = [0.5, 1.0, 2.0, 3.0]
        buttons = []
        for index, value in enumerate(values):
            row = index // 2
            col = index % 2
            bx = x + col * (width + 12)
            by = y + row * (height + 12)
            label = f"{value:.1f}s"
            buttons.append(SpriteButton((bx, by, width, height), label, value))
        return buttons

    def draw(self, win):
        win.blit(self.background, self.rect)

        # Lagt oven på baggrunden, så panelteksten står tydeligt uden at miste sprite-stilen.
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((20, 26, 20, 178))
        win.blit(overlay, self.rect.topleft)

        self._draw_text(win, "Menu", self.title_font, TEXT_COLOR, self.board_width + 20, 24)

        self._draw_text(win, "Spillerfarve", self.header_font, TEXT_COLOR, self.board_width + 20, 88)
        for index, button in enumerate(self.color_buttons):
            selected = self.settings.player_color == button.value
            button.draw(win, self.body_font, selected=selected, alternate=bool(index % 2))

        self._draw_text(win, "AI styring", self.header_font, TEXT_COLOR, self.board_width + 20, 262)
        for index, button in enumerate(self.mode_buttons):
            selected = self.settings.search_mode == button.value
            button.draw(win, self.body_font, selected=selected, alternate=bool(index % 2))

        if self.settings.search_mode == "depth":
            self._draw_text(win, "Valg dybde", self.header_font, TEXT_COLOR, self.board_width + 20, 414)
            for index, button in enumerate(self.depth_buttons):
                selected = self.settings.depth == button.value
                button.draw(win, self.meta_font, selected=selected, alternate=bool(index % 2))
            info = f"Aktiv: dybde {self.settings.depth}"
        else:
            self._draw_text(win, "Valg tid", self.header_font, TEXT_COLOR, self.board_width + 20, 414)
            for index, button in enumerate(self.time_buttons):
                selected = self.settings.time_seconds == button.value
                button.draw(win, self.meta_font, selected=selected, alternate=bool(index % 2))
            info = f"Aktiv: {self.settings.time_seconds:.1f}s pr. traek"

        self._draw_text(win, info, self.meta_font, MUTED_TEXT_COLOR, self.board_width + 20, 578)

    def _draw_text(self, win, text, font, color, x, y):
        surface = font.render(text, True, color)
        win.blit(surface, (x, y))

    def handle_click(self, pos):
        if not self.rect.collidepoint(pos):
            return False

        for button in self.color_buttons:
            if button.contains(pos):
                self.settings.player_color = button.value
                return True

        for button in self.mode_buttons:
            if button.contains(pos):
                self.settings.search_mode = button.value
                return True

        if self.settings.search_mode == "depth":
            for button in self.depth_buttons:
                if button.contains(pos):
                    self.settings.depth = button.value
                    return True
        else:
            for button in self.time_buttons:
                if button.contains(pos):
                    self.settings.time_seconds = button.value
                    return True

        return True