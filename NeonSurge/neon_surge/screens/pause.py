from __future__ import annotations
from typing import Optional

import pygame

from .base       import Screen
from ..constants import SCREEN_W, SCREEN_H, C_WHITE, C_NEON_GRN, C_BLOOD_RED, MODE_RACE, MODE_RACE_HC
from ..utils     import draw_text, draw_dynamic_button


class PauseScreen(Screen):
    """Overlay drawn on top of the frozen game frame."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.sel = 0
        self._hitboxes: list = []

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "JOGANDO"
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
        return "JOGANDO" if self.sel == 0 else "MENU_MODO"

    def update(self, dt: float) -> Optional[str]:
        h = self._hover_sel(self._hitboxes)
        if h is not None:
            self.sel = h
        return None

    def draw(self, surf) -> None:
        f = self.game.fonts
        cx, cy = SCREEN_W // 2, SCREEN_H // 2

        # Draw the frozen game state behind the overlay
        level = self.game.level
        level.draw(surf)
        from .game_screen import GameScreen
        gs: GameScreen = self.game.screens["JOGANDO"]   # type: ignore[assignment]
        t = (self.game.race_timer + level.elapsed
             if self.game.current_mode in (MODE_RACE, MODE_RACE_HC)
             else level.elapsed)
        gs.hud.draw(surf, f, self.game.current_mode, level.phase, t, level.player.dash)

        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        draw_text(surf, "SISTEMA PAUSADO", f["title"], C_WHITE, cx, cy - 100)
        self._hitboxes = [
            draw_dynamic_button(surf, "CONTINUAR [ESC]",   f["sub"], C_NEON_GRN,  cx, cy + 30,  self.sel == 0),
            draw_dynamic_button(surf, "ABANDONAR PARTIDA", f["sub"], C_BLOOD_RED, cx, cy + 120, self.sel == 1),
        ]
