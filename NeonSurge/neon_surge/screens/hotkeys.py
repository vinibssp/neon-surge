from __future__ import annotations
import time
from typing import Optional

import pygame

from .base       import Screen
from ..constants import SCREEN_W, SCREEN_H, C_NEON_GRN, C_NEON_CYN, C_NEON_PNK, C_WHITE
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button


class HotkeysScreen(Screen):
    """Keyboard reference screen shown before each new game session."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "MENU_MODO"
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "TELA_INIMIGOS"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover_sel(self._hitboxes) is not None:
                return "TELA_INIMIGOS"
        return None

    def update(self, dt: float) -> Optional[str]:
        return None

    def draw(self, surf) -> None:
        f = self.game.fonts
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        draw_cyberpunk_bg(surf, time.time())
        self._draw_vol(surf)
        self._back_button(surf)

        draw_text(surf, "CONTROLES DO SISTEMA", f["title"], C_NEON_GRN, cx, 100)

        cmds = [
            ("W A S D / SETAS", "Mover a Nave"),
            ("BARRA DE ESPAÇO", "DASH (Invencibilidade Rápida)"),
            ("TECLA ESC",       "Pausar ou Voltar Menus"),
            ("TECLA F11",       "Ativar/Desativar Tela Cheia"),
        ]
        for i, (key, desc) in enumerate(cmds):
            y = 240 + i * 70
            draw_text(surf, key,         f["sub"],  C_NEON_CYN, cx - 40, y, "direita")
            draw_text(surf, "- " + desc, f["text"], C_WHITE,    cx + 40, y, "esquerda")

        self._hitboxes = [
            draw_dynamic_button(surf, "AVANÇAR PARA AMEAÇAS", f["sub"], C_NEON_PNK,
                                cx, cy + 240, True)
        ]
