import pygame
from .base import AIBehaviour


class ChaserAI(AIBehaviour):
    """Caçador — smoothly lerps toward the player (heat-seeking)."""

    def __init__(self, speed: float) -> None:
        self.speed = speed
        self.dir   = pygame.math.Vector2(0, 0)

    def update(self, transform, player_pos, peers, dt, particle_pool, sound_manager):
        to_player = player_pos - transform.pos
        if to_player.length() > 0:
            desired  = to_player.normalize() * (self.speed * 0.7)
            self.dir = self.dir.lerp(desired, 0.1)
        transform.pos += self.dir
        self._clamp_pos(transform.pos, 12)
