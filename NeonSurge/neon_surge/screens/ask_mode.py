from __future__ import annotations
import time
from typing import Optional

import pygame

from .base       import Screen
from ..constants import SCREEN_W, SCREEN_H, C_NEON_GRN, C_NEON_CYN, C_NEON_PNK
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button


class AskModeScreen(Screen):
    """Shown after game-over when a new pilot name was entered.
    Lets the player keep the same mode or choose a new one."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.sel = 0
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "INPUT_NOME"
            if event.key == pygame.K_RETURN:
                return self._action()
            self.sel = self._nav_keys(event, self.sel, max(1, len(self._hitboxes)))
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            h = self._hover_sel(self._hitboxes)
            if h is not None:
                self.sel = h
                return self._action()
        return None

    def _action(self) -> str:
        self.game.came_from_game_over = False
        return "TELA_INIMIGOS" if self.sel == 0 else "MENU_MODO"

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
        self._back_button(surf)

        draw_text(surf, "NOVO PILOTO REGISTRADO", f["title"], C_NEON_GRN, cx, cy - 100)
        mode_fmt = self.game.current_mode.replace("_", " ")
        self._hitboxes = [
            draw_dynamic_button(surf, f"CONTINUAR EM: {mode_fmt}", f["sub"], C_NEON_CYN,
                                cx, cy + 30,  self.sel == 0),
            draw_dynamic_button(surf, "ESCOLHER NOVO MODO",         f["sub"], C_NEON_PNK,
                                cx, cy + 120, self.sel == 1),
        ]
