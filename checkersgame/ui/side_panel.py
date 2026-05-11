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
DISABLED_TEXT_COLOR = (155, 155, 145)
DISABLED_BG = (52, 55, 49)
DISABLED_BORDER = (92, 94, 84)


@dataclass
class PanelSettings:
    player_color: PieceColor = PieceColor.BLACK
    depth: int = 4
    time_seconds: float = 1.0
    board_flipped: bool = False
    forced_jump: bool = True


class SpriteButton:
    def __init__(self, rect, label, value, icon=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.value = value
        self.icon = icon

    def draw(self, win, font, selected=False, alternate=False, disabled=False):
        bg = DISABLED_BG if disabled else (BUTTON_BG_ALT if alternate else BUTTON_BG)
        pygame.draw.rect(win, bg, self.rect, border_radius=12)
        border_color = DISABLED_BORDER if disabled else (SELECTED_BORDER if selected else BUTTON_BORDER)
        border_width = 4 if selected else 2
        pygame.draw.rect(win, border_color, self.rect, border_width, border_radius=12)

        text_x = self.rect.x + 14
        if self.icon is not None:
            icon_rect = self.icon.get_rect()
            icon_rect.centery = self.rect.centery
            icon_rect.left = self.rect.left + 10
            if disabled:
                icon_surface = self.icon.copy()
                icon_surface.fill((130, 130, 130, 220), special_flags=pygame.BLEND_RGBA_MULT)
                win.blit(icon_surface, icon_rect)
            else:
                win.blit(self.icon, icon_rect)
            text_x = icon_rect.right + 8

        text_color = DISABLED_TEXT_COLOR if disabled else TEXT_COLOR
        text_surface = font.render(self.label, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = text_x
        win.blit(text_surface, text_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class SpriteInputField:
    def __init__(self, rect, label, initial_text, icon=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.text = initial_text
        self.icon = icon
        self.active = False

    def draw(self, win, label_font, input_font, disabled=False):
        label_color = DISABLED_TEXT_COLOR if disabled else TEXT_COLOR
        label_surface = label_font.render(self.label, True, label_color)
        win.blit(label_surface, (self.rect.x, self.rect.y - 26))

        if disabled:
            bg = DISABLED_BG
        else:
            bg = BUTTON_BG_ALT if self.active else BUTTON_BG
        pygame.draw.rect(win, bg, self.rect, border_radius=10)
        if disabled:
            border_color = DISABLED_BORDER
        else:
            border_color = SELECTED_BORDER if self.active else BUTTON_BORDER
        border_width = 3 if self.active else 2
        pygame.draw.rect(win, border_color, self.rect, border_width, border_radius=10)

        text_x = self.rect.x + 10
        if self.icon is not None:
            icon_rect = self.icon.get_rect()
            icon_rect.centery = self.rect.centery
            icon_rect.left = self.rect.left + 8
            if disabled:
                icon_surface = self.icon.copy()
                icon_surface.fill((130, 130, 130, 220), special_flags=pygame.BLEND_RGBA_MULT)
                win.blit(icon_surface, icon_rect)
            else:
                win.blit(self.icon, icon_rect)
            text_x = icon_rect.right + 8

        display_text = self.text if self.text else "..."
        text_color = DISABLED_TEXT_COLOR if disabled else TEXT_COLOR
        text_surface = input_font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = text_x
        win.blit(text_surface, text_rect)

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def set_active(self, is_active):
        self.active = is_active

    def handle_key(self, event):
        if not self.active:
            return False

        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return True

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB, pygame.K_ESCAPE):
            return True

        if event.unicode and event.unicode in "0123456789.":
            if event.unicode == "." and "." in self.text:
                return True
            self.text += event.unicode
            return True

        return False


class SidePanel:
    def __init__(self, board_width, height):
        self.board_width = board_width
        self.height = height
        self.rect = pygame.Rect(board_width, 0, PANEL_WIDTH, height)
        self.settings = PanelSettings()
        self.settings_locked = False
        self.start_button_visible = False

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
        self.depth_input, self.time_input = self._build_input_fields()
        self.forced_jump_button = self._build_forced_jump_button()
        self.start_button = self._build_start_button()
        self.flip_button = self._build_flip_button()
        self.restart_button = self._build_restart_button()

    def _clear_input_focus(self):
        self.depth_input.set_active(False)
        self.time_input.set_active(False)

    def set_settings_locked(self, locked):
        self.settings_locked = locked
        if locked:
            self._clear_input_focus()

    def set_start_button_visible(self, visible):
        self.start_button_visible = visible

    def _load_image(self, name, size):
        image = pygame.image.load(str(ASSETS_DIR / name)).convert_alpha()
        return pygame.transform.smoothscale(image, size)

    def _build_color_buttons(self):
        x = self.board_width + 20
        y = 124
        width = PANEL_WIDTH - 40
        height = 52
        return [
            SpriteButton((x, y, width, height), "Sort", PieceColor.BLACK, self.black_icon),
            SpriteButton((x, y + 68, width, height), "Hvid", PieceColor.WHITE, self.white_icon),
        ]

    def _build_input_fields(self):
        x = self.board_width + 20
        y = 370
        width = PANEL_WIDTH - 40
        height = 42
        depth_field = SpriteInputField((x, y, width, height), "Dybde", str(self.settings.depth), self.depth_icon)
        time_field = SpriteInputField((x, y + 78, width, height), "Tid i sekunder", f"{self.settings.time_seconds:.1f}", self.time_icon)
        return depth_field, time_field

    def _build_forced_jump_button(self):
        x = self.board_width + 20
        y = 302
        width = PANEL_WIDTH - 40
        height = 42
        return SpriteButton((x, y, width, height), "Forced jump: ON", "forced_jump")

    def _build_start_button(self):
        x = self.board_width + 20
        y = 472
        width = PANEL_WIDTH - 40
        height = 44
        return SpriteButton((x, y, width, height), "Start spil", "start")

    def _build_flip_button(self):
        x = self.board_width + 20
        y = 524
        width = PANEL_WIDTH - 40
        height = 44
        return SpriteButton((x, y, width, height), "Flip board", "flip")

    def _build_restart_button(self):
        x = self.board_width + 20
        y = 576
        width = PANEL_WIDTH - 40
        height = 44
        return SpriteButton((x, y, width, height), "Genstart spil", "restart")

    def _apply_depth_text(self):
        try:
            depth = int(self.depth_input.text)
        except ValueError:
            return False

        depth = max(1, min(20, depth))
        self.settings.depth = depth
        self.depth_input.text = str(depth)
        return True

    def _apply_time_text(self):
        try:
            time_seconds = float(self.time_input.text)
        except ValueError:
            return False

        time_seconds = max(0.1, min(60.0, time_seconds))
        self.settings.time_seconds = time_seconds
        self.time_input.text = f"{time_seconds:.2f}".rstrip("0").rstrip(".")
        return True

    def draw(self, win):
        win.blit(self.background, self.rect)

        # Lagt oven på baggrunden, så panelteksten står tydeligt uden at miste sprite-stilen.
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((20, 26, 20, 178))
        win.blit(overlay, self.rect.topleft)

        self._draw_text(win, "Menu", self.title_font, TEXT_COLOR, self.board_width + 20, 24)

        if self.settings_locked:
            self._draw_text(win, "Laast mens spillet koerer", self.meta_font, MUTED_TEXT_COLOR, self.board_width + 20, 64)

        self._draw_text(win, "Spillerfarve", self.header_font, TEXT_COLOR, self.board_width + 20, 88)
        for index, button in enumerate(self.color_buttons):
            selected = self.settings.player_color == button.value
            button.draw(
                win,
                self.body_font,
                selected=selected,
                alternate=bool(index % 2),
                disabled=self.settings_locked,
            )

        self._draw_text(win, "AI indstillinger", self.header_font, TEXT_COLOR, self.board_width + 20, 262)
        self.forced_jump_button.label = "Forced jump: ON" if self.settings.forced_jump else "Forced jump: OFF"
        self.forced_jump_button.draw(
            win,
            self.meta_font,
            selected=self.settings.forced_jump,
            disabled=self.settings_locked,
        )
        self.depth_input.draw(win, self.meta_font, self.body_font, disabled=self.settings_locked)
        self.time_input.draw(win, self.meta_font, self.body_font, disabled=self.settings_locked)

        if self.start_button_visible:
            self.start_button.draw(win, self.body_font)

        self.flip_button.draw(win, self.body_font, selected=self.settings.board_flipped)
        self.restart_button.draw(win, self.body_font)

    def _draw_text(self, win, text, font, color, x, y):
        surface = font.render(text, True, color)
        win.blit(surface, (x, y))

    def handle_click(self, pos):
        if not self.rect.collidepoint(pos):
            self._clear_input_focus()
            return None

        for button in self.color_buttons:
            if button.contains(pos):
                if self.settings_locked:
                    self._clear_input_focus()
                    return "panel"
                self.settings.player_color = button.value
                self._clear_input_focus()
                return "settings"

        if self.depth_input.contains(pos):
            if self.settings_locked:
                self._clear_input_focus()
                return "panel"
            self.depth_input.set_active(True)
            self.time_input.set_active(False)
            return "settings"

        if self.time_input.contains(pos):
            if self.settings_locked:
                self._clear_input_focus()
                return "panel"
            self.time_input.set_active(True)
            self.depth_input.set_active(False)
            return "settings"

        if self.forced_jump_button.contains(pos):
            if self.settings_locked:
                self._clear_input_focus()
                return "panel"
            self.settings.forced_jump = not self.settings.forced_jump
            self._clear_input_focus()
            return "settings"

        if self.flip_button.contains(pos):
            self.settings.board_flipped = not self.settings.board_flipped
            self._clear_input_focus()
            return "settings"

        if self.restart_button.contains(pos):
            self._clear_input_focus()
            return "restart"

        if self.start_button_visible and self.start_button.contains(pos):
            self._clear_input_focus()
            return "start"

        self._clear_input_focus()
        return "panel"

    def handle_keydown(self, event):
        if self.settings_locked:
            return False

        consumed = False

        if self.depth_input.active:
            consumed = self.depth_input.handle_key(event)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self._apply_depth_text()
                self.depth_input.set_active(False)
                self.time_input.set_active(True)
                return True
            if event.key == pygame.K_ESCAPE:
                self._apply_depth_text()
                self.depth_input.set_active(False)
                return True
            if consumed:
                self._apply_depth_text()
                return True

        if self.time_input.active:
            consumed = self.time_input.handle_key(event)
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                self._apply_time_text()
                self.time_input.set_active(False)
                return True
            if event.key == pygame.K_ESCAPE:
                self._apply_time_text()
                self.time_input.set_active(False)
                return True
            if consumed:
                self._apply_time_text()
                return True

        return False