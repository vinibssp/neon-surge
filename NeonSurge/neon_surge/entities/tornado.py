import pygame
import random
import math

from ..constants import (
    TORNADO_RADIUS, TORNADO_PULL, TORNADO_SLOW, TORNADO_LIFETIME,
    C_WHITE, C_NEON_PNK, C_NEON_CYN
)
from ..utils import draw_neon_glow

class Tornado:
    """
    An environmental hazard that pulls the player and slows them down.
    Appearance is random and temporary.
    """

    def __init__(self, x: float, y: float) -> None:
        self.pos = pygame.math.Vector2(x, y)
        self.radius = TORNADO_RADIUS
        self.lifetime = TORNADO_LIFETIME
        self.angle = 0.0  # Used for visual rotation

    @property
    def expired(self) -> bool:
        return self.lifetime <= 0

    def update(self, player, dt: float) -> None:
        self.lifetime -= dt
        self.angle += 360 * dt  # Rotate 360 degrees per second

        dist = self.pos.distance_to(player.pos)
        if dist < self.radius:
            # Pull effect
            pull_dir = (self.pos - player.pos).normalize()
            # The closer, the stronger the pull? Let's make it constant for now or slightly inverse.
            # Constant pull as requested.
            player.transform.pos += pull_dir * TORNADO_PULL * dt
            
            # Slow effect - reduce velocity
            player.transform.vel *= TORNADO_SLOW

    def draw(self, surf) -> None:
        # Draw a swirling effect
        color = C_NEON_PNK
        draw_neon_glow(surf, color, self.pos.x, self.pos.y, 20, 5)
        
        # Draw multiple arcs or spirals to simulate a tornado
        for i in range(3):
            rot_angle = math.radians(self.angle + i * 120)
            for r in range(10, int(self.radius), 20):
                # Scale alpha or thickness by lifetime? 
                alpha = int(255 * (self.lifetime / TORNADO_LIFETIME))
                point_angle = rot_angle + (r * 0.05)
                px = self.pos.x + math.cos(point_angle) * r
                py = self.pos.y + math.sin(point_angle) * r
                
                size = 2 + (r // 40)
                pygame.draw.circle(surf, color, (int(px), int(py)), size)

        # Draw center core
        pygame.draw.circle(surf, C_WHITE, (int(self.pos.x), int(self.pos.y)), 5)
