"""
neon_surge/level.py
===================
Single game session / phase manager.

Knows nothing about menus, audio, fonts or the display pipeline.
Communicates outcomes upward via the read-only `outcome` property.
"""
from __future__ import annotations

import random
from typing import List, Optional

import pygame

from .constants import (
    SCREEN_W, SCREEN_H, HUD_H,
    MODE_RACE, MODE_RACE_HC, MODE_SURV, MODE_HC,
    ENEMY_BASE_SPEED,
    SURV_SPAWN_INTERVAL, SURV_MAX_SPEED, SURV_SPEED_GROWTH,
    HC_SPAWN_INTERVAL,   HC_MAX_SPEED,   HC_SPEED_GROWTH,
    C_BG,
)
from .utils             import draw_game_grid
from .entities          import Player, Enemy, Collectible, Portal
from .systems           import ParticleSystem, SpawnSystem, CollisionSystem


class Level:
    """
    Spawns and ticks all gameplay entities for one phase.

    Outcome values
    --------------
    None          — still running
    "DIED"        — player was hit
    "PHASE_CLEAR" — race mode, portal reached, more phases remain
    "WIN"         — race mode, phase 10 portal reached
    """

    KINDS = ["quique", "perseguidor", "investida"]

    def __init__(self, mode: str, phase: int) -> None:
        self.mode   = mode
        self.phase  = phase

        self.player            = Player(SCREEN_W // 2, SCREEN_H // 2)
        self.enemies:      List[Enemy]       = []
        self.collectibles: List[Collectible] = []
        self.portal:       Optional[Portal]  = None

        self.particles  = ParticleSystem()
        self.collision  = CollisionSystem()
        self.elapsed    = 0.0
        self.shake_frames = 0
        self._outcome: Optional[str] = None

        if mode == MODE_SURV:
            self._spawner: Optional[SpawnSystem] = SpawnSystem(
                SURV_SPAWN_INTERVAL, SURV_MAX_SPEED, SURV_SPEED_GROWTH)
        elif mode == MODE_HC:
            self._spawner = SpawnSystem(
                HC_SPAWN_INTERVAL, HC_MAX_SPEED, HC_SPEED_GROWTH)
        else:
            self._spawner = None

        self._setup()

    # ── setup ─────────────────────────────────────────────────────────────────

    def _setup(self) -> None:
        if self.mode in (MODE_RACE, MODE_RACE_HC):
            for _ in range(5):
                x = random.randint(50, SCREEN_W - 50)
                y = random.randint(HUD_H + 50, SCREEN_H - 50)
                self.collectibles.append(Collectible(x, y))
            self._spawn_enemies(3 + self.phase, ENEMY_BASE_SPEED + self.phase * 0.3)
        elif self.mode == MODE_SURV:
            self._spawn_enemies(2, ENEMY_BASE_SPEED)
        elif self.mode == MODE_HC:
            self._spawn_enemies(4, ENEMY_BASE_SPEED + 2)

    def _spawn_enemies(self, count: int, speed: float) -> None:
        for _ in range(count):
            ex, ey = self.player.pos.x, self.player.pos.y
            while abs(ex - self.player.pos.x) < 300 and abs(ey - self.player.pos.y) < 300:
                ex = random.randint(50, SCREEN_W - 50)
                ey = random.randint(HUD_H + 50, SCREEN_H - 50)
            kind = random.choice(self.KINDS)
            self.enemies.append(Enemy(ex, ey, kind, speed))

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, keys, dt: float) -> None:
        if self._outcome:
            return

        self.elapsed += dt

        dashed = self.player.update(keys, self.particles.pool)
        if dashed:
            self.shake_frames = 6

        for e in self.enemies:
            e.update(self.player.pos, self.enemies, dt, self.particles.pool)

        self.particles.update()

        if self.shake_frames > 0:
            self.shake_frames -= 1

        if self.collision.player_vs_enemies(self.player, self.enemies):
            self.shake_frames = 15
            self._outcome = "DIED"
            return

        if self.mode in (MODE_RACE, MODE_RACE_HC):
            self._update_race()
        else:
            self._update_survival(dt)

    def _update_race(self) -> None:
        hit = self.collision.player_vs_collectible(self.player, self.collectibles)
        if hit:
            hit.emitter.burst(hit.pos.x, hit.pos.y, self.particles.pool)
            self.collectibles.remove(hit)
            self.shake_frames = 2

        if not self.collectibles and self.portal is None:
            self.portal = Portal(SCREEN_W // 2, HUD_H + 80)
            self.shake_frames = 10

        if self.collision.player_vs_portal(self.player, self.portal):
            self._outcome = "WIN" if self.phase >= 10 else "PHASE_CLEAR"

    def _update_survival(self, dt: float) -> None:
        count = self._spawner.update(dt)
        if count:
            speed = self._spawner.current_speed(self.elapsed)
            self._spawn_enemies(count, speed)
            self.shake_frames = 3 if self.mode == MODE_SURV else 5

    # ── outcome ───────────────────────────────────────────────────────────────

    @property
    def outcome(self) -> Optional[str]:
        return self._outcome

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surf) -> None:
        import random as _r
        ox = _r.randint(-8, 8) if self.shake_frames > 0 else 0
        oy = _r.randint(-8, 8) if self.shake_frames > 0 else 0

        blur = pygame.Surface((SCREEN_W, SCREEN_H))
        blur.fill(C_BG)
        blur.set_alpha(80)
        surf.blit(blur, (0, 0))

        game_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        draw_game_grid(game_surf)

        for c in self.collectibles:
            c.draw(game_surf)
        if self.portal:
            self.portal.draw(game_surf)
        self.particles.draw(game_surf)
        for e in self.enemies:
            e.draw(game_surf)
        self.player.draw(game_surf)

        surf.blit(game_surf, (ox, oy))
