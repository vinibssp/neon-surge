from __future__ import annotations
import time
from typing import Optional

import pygame

from .base       import Screen
from ..constants import SCREEN_W, SCREEN_H, C_GOLD, C_NEON_CYN, C_NEON_PNK, C_BLOOD_RED, C_WHITE, C_NEON_GRN
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button, make_panel


class InfoModesScreen(Screen):
    """Explains all four game modes in a scrollable-style panel."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                return "MENU_MODO"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover_sel(self._hitboxes) is not None:
                return "MENU_MODO"
        return None

    def update(self, dt: float) -> Optional[str]:
        return None

    def draw(self, surf) -> None:
        f = self.game.fonts
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        draw_cyberpunk_bg(surf, time.time())
        self._draw_vol(surf)
        self._back_button(surf)

        draw_text(surf, "MANUAL DOS MODOS DE JOGO", f["title"], C_GOLD, cx, 60)

        pw = min(1150, SCREEN_W - 40)
        ph = min(460,  SCREEN_H - 200)
        pr = pygame.Rect(0, 0, pw, ph)
        pr.center = (cx, cy - 20)
        surf.blit(make_panel(pw, ph), pr.topleft)

        xl = pr.left + 50
        entries = [
            ("MODO CORRIDA:",                C_NEON_CYN,
             "Complete 10 fases no menor tempo. Se morrer, você repete apenas a fase atual."),
            ("MODO CORRIDA HARDCORE:",       C_NEON_CYN,
             "Complete 10 fases. Se a nave for destruída, VOCÊ VOLTA PARA A FASE 1 e o tempo zera!"),
            ("MODO SOBREVIVÊNCIA:",          C_NEON_PNK,
             "Sobreviva o máximo que puder. Inimigos surgem e ficam mais rápidos com o tempo."),
            ("MODO SOBREVIVÊNCIA HARDCORE:", C_BLOOD_RED,
             "Inimigos nascem o dobro de rápido e a velocidade de movimento cresce drasticamente."),
        ]
        for i, (title, color, desc) in enumerate(entries):
            y = pr.top + 40 + i * 100
            draw_text(surf, title, f["sub"],  color,   xl, y,      "esquerda")
            draw_text(surf, desc,  f["desc"], C_WHITE, xl, y + 35, "esquerda")

        self._hitboxes = [
            draw_dynamic_button(surf, "VOLTAR PARA O MENU", f["sub"], C_NEON_GRN,
                                cx, cy + 280, True)
        ]
