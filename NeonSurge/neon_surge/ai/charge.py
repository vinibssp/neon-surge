import pygame

from ..constants import SCREEN_W, SCREEN_H, HUD_H, ENEMY_CHARGE_MULT, C_NEON_ORG
from .base import AIBehaviour


class ChargeAI(AIBehaviour):
    """
    Kamikaze — three-state machine: WAIT → AIM (tracks player) → CHARGE.

    Transitions:
        WAIT   → AIM    after 1.2 s
        AIM    → CHARGE after 0.9 s  (target locked at 0.5 s)
        CHARGE → WAIT   after 0.6 s  (or on wall collision)
    """

    WAIT   = "ESPERANDO"
    AIM    = "MIRANDO"
    CHARGE = "ATACANDO"

    def __init__(self, speed: float) -> None:
        self.speed  = speed
        self.state  = self.WAIT
        self.timer  = 0.0
        self.target = pygame.math.Vector2(0, 0)
        self.locked = False
        self.dir    = pygame.math.Vector2(0, 0)

    def update(self, transform, player_pos, peers, dt, particle_pool):
        self.timer += dt
        pos = transform.pos
        r   = 12

        if self.state == self.WAIT:
            self.dir    = self.dir.lerp(pygame.math.Vector2(0, 0), 0.1)
            self.locked = False
            if self.timer > 1.2:
                self.state = self.AIM
                self.timer = 0.0

        elif self.state == self.AIM:
            if self.timer < 0.5:
                self.target = pygame.math.Vector2(player_pos)
            else:
                self.locked = True
            if self.timer > 0.9:
                vec = self.target - pos
                if vec.length() > 0:
                    self.dir = vec.normalize() * (self.speed * ENEMY_CHARGE_MULT)
                self.state = self.CHARGE
                self.timer = 0.0

        elif self.state == self.CHARGE:
            if particle_pool is not None:
                from neon_surge.entities.particle import Particle
                particle_pool.append(Particle(pos.x, pos.y, C_NEON_ORG))
            if self.timer > 0.6:
                self.state = self.WAIT
                self.timer = 0.0

        pos += self.dir

        hit_wall = False
        if   pos.x <= r:            pos.x = r;            hit_wall = True
        elif pos.x >= SCREEN_W - r: pos.x = SCREEN_W - r; hit_wall = True
        if   pos.y <= HUD_H + r:    pos.y = HUD_H + r;    hit_wall = True
        elif pos.y >= SCREEN_H - r: pos.y = SCREEN_H - r; hit_wall = True

        if hit_wall and self.state == self.CHARGE:
            self.state = self.WAIT
            self.timer = 0.0
