from __future__ import annotations
import time
from typing import Optional

import pygame

from .base       import Screen
from ..constants import (
    SCREEN_W, SCREEN_H,
    C_WHITE, C_NEON_GRN, C_NEON_CYN, C_NEON_PNK, C_BLOOD_RED, C_GOLD, C_DARK_GRAY,
)
from ..utils     import draw_text, draw_cyberpunk_bg, draw_dynamic_button, make_panel


class RankingScreen(Screen):
    """Game-over / victory screen with personal result and top-5 leaderboard."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.sel = 0
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
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
        if self.sel == 0:
            self.game.start_level(phase=1)
            return "JOGANDO"
        if self.sel == 1:
            return "MENU_MODO"
        # sel == 2 → new pilot
        self.game.player_name         = ""
        self.game.came_from_game_over  = True
        return "INPUT_NOME"

    def update(self, dt: float) -> Optional[str]:
        h = self._hover_sel(self._hitboxes)
        if h is not None:
            self.sel = h
        return None

    def draw(self, surf) -> None:
        f = self.game.fonts
        cx, cy  = SCREEN_W // 2, SCREEN_H // 2
        ranking = self.game.ranking
        mode    = self.game.current_mode

        draw_cyberpunk_bg(surf, time.time())
        self._draw_vol(surf)

        title_color = (C_BLOOD_RED if "HARDCORE" in mode
                       else C_NEON_GRN  if "CORRIDA" in mode
                       else C_NEON_PNK)
        draw_text(surf, f"GAME OVER — {mode.replace('_', ' ')}", f["title"], title_color, cx, 50)

        pw, ph = 700, 410
        rr = pygame.Rect(0, 0, pw, ph)
        rr.center = (cx, cy - 50)
        surf.blit(make_panel(pw, ph), rr.topleft)

        draw_text(surf, "DESEMPENHO DA MISSÃO:", f["sub"], C_NEON_GRN, cx, rr.top + 25)
        draw_text(surf,
                  f"Tempo: {ranking.last_time:.1f}s    |    Sua Posição: {ranking.last_pos}º Lugar",
                  f["sub"], C_WHITE, cx, rr.top + 60)
        pygame.draw.line(surf, C_DARK_GRAY,
                         (rr.left + 50, rr.top + 95), (rr.right - 50, rr.top + 95), 2)

        draw_text(surf, f"--- TOP 5 {mode.replace('_', ' ')} ---",
                  f["sub"], C_NEON_CYN, cx, rr.top + 130)

        last_id = ranking.last_record_id(mode)
        for i, rec in enumerate(ranking.top(mode)):
            color = C_GOLD if rec.get("id", 0) == last_id else C_WHITE
            y     = rr.top + 180 + i * 40
            draw_text(surf, f"{i + 1}º {rec['nome']}", f["sub"], color, rr.left + 80,  y, "esquerda")
            draw_text(surf, f"{rec['tempo']:.1f}s",     f["sub"], color, rr.right - 80, y, "direita")

        self._hitboxes = [
            draw_dynamic_button(surf, "JOGAR NOVAMENTE (MESMO MODO)", f["sub"], C_NEON_GRN,  cx, rr.bottom + 40,  self.sel == 0),
            draw_dynamic_button(surf, "MANTER PILOTO (MUDAR MODO)",   f["sub"], C_NEON_CYN,  cx, rr.bottom + 110, self.sel == 1),
            draw_dynamic_button(surf, "CRIAR NOVO PILOTO",             f["sub"], C_NEON_PNK,  cx, rr.bottom + 180, self.sel == 2),
        ]
