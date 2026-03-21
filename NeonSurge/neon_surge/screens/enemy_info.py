from __future__ import annotations
import time
from typing import Optional

import pygame

from .base       import Screen
from ..constants import SCREEN_W, SCREEN_H, C_BLOOD_RED, C_NEON_PNK, C_NEON_ORG, C_WHITE, C_LT_GRAY, C_NEON_GRN
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button, make_panel, draw_neon_glow


class EnemyInfoScreen(Screen):
    """Enemy codex — describes the three drone types before the first run."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "TELA_HOTKEYS"
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self._start()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover_sel(self._hitboxes) is not None:
                return self._start()
        return None

    def _start(self) -> str:
        self.game.start_level(phase=1)
        return "JOGANDO"

    def update(self, dt: float) -> Optional[str]:
        return None

    def draw(self, surf) -> None:
        f = self.game.fonts
        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        draw_cyberpunk_bg(surf, time.time())
        self._draw_vol(surf)
        self._back_button(surf)

        draw_text(surf, "ARQUIVO DE AMEAÇAS", f["title"], C_BLOOD_RED, cx, 60)

        pw = min(1100, SCREEN_W - 40)
        ph = min(480,  SCREEN_H - 200)
        pr = pygame.Rect(0, 0, pw, ph)
        pr.center = (cx, cy - 10)
        surf.blit(make_panel(pw, ph), pr.topleft)

        xl = pr.left + 150
        entries = [
            (C_NEON_PNK,  "SENTINELA (O Básico):",
             "Patrulha a área rebatendo nas paredes.",
             "Cuidado com o efeito manada quando eles se agrupam."),
            (C_BLOOD_RED, "CAÇADOR (A Sanguessuga):",
             "Possui navegação autônoma avançada.",
             "Persegue sua assinatura de calor continuamente, tente despistá-lo."),
            (C_NEON_ORG,  "KAMIKAZE (O Fuzil):",
             "Aguarde o feixe de mira vermelho aparecer, indicando que ele travou no alvo.",
             "Espere o disparo e use o Dash (Espaço) no momento exato para esquivar!"),
        ]
        for i, (color, title, line1, line2) in enumerate(entries):
            y  = pr.top + 50 + i * 140
            ix, iy = pr.left + 80, y + 20
            draw_neon_glow(surf, color, ix, iy, 18, 2)
            pygame.draw.circle(surf, color,   (ix, iy), 18)
            pygame.draw.circle(surf, C_WHITE, (ix, iy), 6)
            draw_text(surf, title, f["sub"],  color,     xl, y,      "esquerda")
            draw_text(surf, line1, f["desc"], C_WHITE,   xl, y + 35, "esquerda")
            draw_text(surf, line2, f["desc"], C_LT_GRAY, xl, y + 65, "esquerda")

        self._hitboxes = [
            draw_dynamic_button(surf, "INICIAR SEQUÊNCIA DE JOGO", f["sub"], C_NEON_GRN,
                                cx, cy + 290, True)
        ]
