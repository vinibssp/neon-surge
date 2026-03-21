import math
import random

import pygame

from ..constants import SCREEN_W, SCREEN_H, HUD_H
from .base import AIBehaviour


class BounceAI(AIBehaviour):
    """Sentinela — constant-speed patrol that bounces off all four walls."""

    def __init__(self, speed: float) -> None:
        ang      = random.uniform(0, math.tau)
        self.vel = pygame.math.Vector2(math.cos(ang), math.sin(ang)) * speed

    def update(self, transform, player_pos, peers, dt, particle_pool):
        r   = 12
        pos = transform.pos
        pos += self.vel
        if   pos.x <= r:            pos.x = r;            self.vel.x *= -1
        elif pos.x >= SCREEN_W - r: pos.x = SCREEN_W - r; self.vel.x *= -1
        if   pos.y <= HUD_H + r:    pos.y = HUD_H + r;    self.vel.y *= -1
        elif pos.y >= SCREEN_H - r: pos.y = SCREEN_H - r; self.vel.y *= -1
