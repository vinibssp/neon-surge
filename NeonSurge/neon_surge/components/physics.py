import pygame
from .transform import TransformComponent


class PhysicsComponent:
    """Acceleration + friction + boundary clamping.

    Only the Player uses this; enemies move inside their AI behaviour.
    """

    def __init__(self, accel: float, friction: float) -> None:
        self.accel    = accel
        self.friction = friction

    def apply(
        self,
        transform: TransformComponent,
        direction: pygame.math.Vector2,
        bounds_x: tuple,
        bounds_y: tuple,
    ) -> None:
        if direction.length() > 0:
            transform.vel += direction.normalize() * self.accel
        transform.vel *= self.friction
        transform.pos += transform.vel
        transform.pos.x = max(bounds_x[0], min(bounds_x[1], transform.pos.x))
        transform.pos.y = max(bounds_y[0], min(bounds_y[1], transform.pos.y))
