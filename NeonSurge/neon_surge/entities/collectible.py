import pygame

from ..constants  import C_GOLD
from ..utils      import draw_neon_glow
from ..components import ColliderComponent, ParticleEmitter


class Collectible:
    """Pick-up token — collecting all of them opens the phase portal."""

    def __init__(self, x: float, y: float) -> None:
        self.pos      = pygame.math.Vector2(x, y)
        self.collider = ColliderComponent(20)
        self.emitter  = ParticleEmitter(C_GOLD)

    def draw(self, surf) -> None:
        draw_neon_glow(surf, C_GOLD, self.pos.x, self.pos.y, 6, 2)
        pygame.draw.rect(
            surf, C_GOLD,
            (int(self.pos.x) - 6, int(self.pos.y) - 6, 12, 12),
            border_radius=2,
        )
