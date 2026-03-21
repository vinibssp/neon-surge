import math
import time

import pygame

from ..constants  import C_NEON_GRN
from ..utils      import draw_neon_glow
from ..components import ColliderComponent


class Portal:
    """End-of-phase exit gate — pulsates and appears once all collectibles are taken."""

    def __init__(self, x: float, y: float) -> None:
        self.pos      = pygame.math.Vector2(x, y)
        self.collider = ColliderComponent(30)

    def draw(self, surf) -> None:
        r = 20 + math.sin(time.time() * 10) * 5
        draw_neon_glow(surf, C_NEON_GRN, self.pos.x, self.pos.y, r, 4)
        pygame.draw.circle(
            surf, C_NEON_GRN,
            (int(self.pos.x), int(self.pos.y)),
            int(r), 3,
        )
