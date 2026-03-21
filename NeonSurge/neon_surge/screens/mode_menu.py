from __future__ import annotations
import time
from typing import List, Optional

import pygame

from .base       import Screen
from ..constants import (
    SCREEN_W, SCREEN_H,
    C_WHITE, C_NEON_CYN, C_NEON_PNK, C_BLOOD_RED, C_GOLD, C_LT_GRAY,
    MODE_RACE, MODE_RACE_HC, MODE_SURV, MODE_HC,
)
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button


class ModeMenuScreen(Screen):
    """Main menu — choose a game mode or read the info screen."""

    _ITEMS: List[tuple] = [
        ("CORRIDA (SPEEDRUN)",              C_NEON_CYN,  MODE_RACE),
        ("CORRIDA HARDCORE (PERMADEATH)",   C_NEON_CYN,  MODE_RACE_HC),
        ("SOBREVIVÊNCIA (INFINITO)",        C_NEON_PNK,  MODE_SURV),
        ("SOBREVIVÊNCIA HARDCORE (BRUTAL)", C_BLOOD_RED, MODE_HC),
        ("? ENTENDER OS MODOS ?",           C_GOLD,      None),
    ]

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
            self.sel = self._nav_keys(event, self.sel, len(self._ITEMS))
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            h = self._hover_sel(self._hitboxes)
            if h is not None:
                self.sel = h
                return self._action()
        return None

    def _action(self) -> str:
        _, _, mode = self._ITEMS[self.sel]
        if mode is None:
            return "TELA_INFO_MODOS"
        self.game.current_mode = mode
        return "TELA_HOTKEYS"

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

        draw_text(surf, "SISTEMA PRINCIPAL", f["title"], C_WHITE, cx, cy - 230)
        positions = [cy - 110, cy - 40, cy + 30, cy + 100, cy + 190]
        self._hitboxes = [
            draw_dynamic_button(surf, label, f["sub"], color, cx, y, self.sel == i)
            for i, ((label, color, _), y) in enumerate(zip(self._ITEMS, positions))
        ]
        draw_text(surf, "Navegue com Mouse ou Setas + Enter",
                  f["text"], C_LT_GRAY, cx, SCREEN_H - 40)
