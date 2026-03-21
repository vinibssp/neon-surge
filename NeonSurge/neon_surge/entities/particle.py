import random

import pygame

from ..constants import C_WHITE
from ..utils     import draw_neon_glow


class Particle:
    """Short-lived visual effect — stored in a flat pool inside ParticleSystem."""

    def __init__(self, x: float, y: float, color: tuple) -> None:
        self.pos    = pygame.math.Vector2(x, y)
        self.vel    = pygame.math.Vector2(random.uniform(-3, 3), random.uniform(-3, 3))
        self.radius = random.uniform(4, 7)
        self.color  = color

    def update(self) -> None:
        self.pos    += self.vel
        self.radius -= 0.3

    @property
    def alive(self) -> bool:
        return self.radius > 0

    def draw(self, surf) -> None:
        if self.radius > 0:
            draw_neon_glow(surf, self.color, self.pos.x, self.pos.y, self.radius, 2)
            pygame.draw.circle(
                surf, C_WHITE,
                (int(self.pos.x), int(self.pos.y)),
                max(1, int(self.radius // 2)),
            )
