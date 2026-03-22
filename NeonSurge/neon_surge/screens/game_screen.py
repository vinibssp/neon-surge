from __future__ import annotations
from typing import Optional

import pygame

from .base       import Screen
from ..constants import MODE_RACE, MODE_RACE_HC
from ..hud       import HUD
from ..services.sound import SoundManager


class GameScreen(Screen):
    """Active gameplay screen — delegates all logic to Level."""

    def __init__(self, game) -> None:
        super().__init__(game)
        self.hud = HUD()
        self.game.sound_manager = SoundManager()

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "PAUSA"
        return None

    def update(self, dt: float) -> Optional[str]:
        level = self.game.level
        level.update(pygame.key.get_pressed(), dt, self.game.sound_manager)

        outcome = level.outcome
        if outcome is None:
            return None

        mode = self.game.current_mode

        if outcome == "DIED":
            if mode == MODE_RACE:
                self.game.race_timer += level.elapsed
                self.game.start_level(phase=level.phase)
                return None
            else:
                score = (self.game.race_timer + level.elapsed
                         if mode == MODE_RACE_HC else level.elapsed)
                self.game.ranking.save(mode, self.game.player_name, score)
                return "RANKING"

        if outcome == "PHASE_CLEAR":
            self.game.race_timer += level.elapsed
            self.game.start_level(phase=level.phase + 1)
            return None

        if outcome == "WIN":
            self.game.ranking.save(mode, self.game.player_name,
                                   self.game.race_timer + level.elapsed)
            return "RANKING"

        return None

    def draw(self, surf) -> None:
        level = self.game.level
        level.draw(surf)
        t = (self.game.race_timer + level.elapsed
             if self.game.current_mode in (MODE_RACE, MODE_RACE_HC)
             else level.elapsed)
        self.hud.draw(surf, self.game.fonts, self.game.current_mode,
                      level.phase, t, level.player.dash)
