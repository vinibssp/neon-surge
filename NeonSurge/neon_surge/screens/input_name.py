from __future__ import annotations
import time
from typing import Optional

import pygame

from .base       import Screen
from ..constants import SCREEN_W, SCREEN_H, C_NEON_CYN, C_NEON_GRN, C_WHITE, C_DARK_BLUE
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button


class InputNameScreen(Screen):
    """First screen — pilot name entry."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.sel = 0
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            k = event.key
            if k == pygame.K_BACKSPACE:
                self.game.player_name = self.game.player_name[:-1]
            elif k == pygame.K_RETURN:
                return self._confirm()
            elif (
                len(self.game.player_name) < 12
                and event.unicode.isprintable()
                and k not in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
            ):
                self.game.player_name += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if any(r.collidepoint(*self.game.mouse_pos()) for r in self._hitboxes):
                return self._confirm()
        return None

    def _confirm(self) -> Optional[str]:
        if not self.game.player_name:
            return None
        if self.game.came_from_game_over and self.game.current_mode:
            return "PERGUNTA_MODO"
        return "MENU_MODO"

    def update(self, dt: float) -> Optional[str]:
        h = self._hover_sel(self._hitboxes)
        if h is not None:
            self.sel = h
        return None

    def draw(self, surf) -> None:
        f = self.game.fonts
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        draw_cyberpunk_bg(surf, time.time())
        self._draw_vol(surf)

        draw_text(surf, "NEON SURGE",               f["title"], C_NEON_CYN, cx, cy - 140)
        draw_text(surf, "IDENTIFICAÇÃO DO PILOTO:", f["text"],  C_WHITE,    cx, cy - 20)

        box = pygame.Rect(0, 0, 400, 60)
        box.center = (cx, cy + 40)
        pygame.draw.rect(surf, C_DARK_BLUE, box, border_radius=10)
        pygame.draw.rect(surf, C_NEON_GRN,  box, 2, border_radius=10)
        cursor = "_" if int(time.time() * 2) % 2 == 0 else ""
        draw_text(surf, self.game.player_name + cursor, f["sub"], C_NEON_GRN, cx, cy + 40)

        self._hitboxes = [
            draw_dynamic_button(surf, "CONFIRMAR DADOS", f["text"], C_NEON_GRN,
                                cx, cy + 180, self.sel == 0)
        ]
