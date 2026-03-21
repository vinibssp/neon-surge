import pygame


class TransformComponent:
    """2-D position and velocity — the minimal spatial state every entity needs."""

    def __init__(self, x: float, y: float) -> None:
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
